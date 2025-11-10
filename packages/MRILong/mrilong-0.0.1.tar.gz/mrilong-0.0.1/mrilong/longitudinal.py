from __future__ import annotations
import csv
import json
import os
from dataclasses import dataclass
from .paths import make_timestamped_output_dir
from typing import Dict, List, Tuple

import numpy as np

from .config import get as cfg
from .io import load_nifti_as_ras, save_nifti, zscore_normalize, percentile_clip, maybe_centerpad_h_axis_to_cube, load_raw_then_crop_then_ras
from .infer import run_skull_strip, run_segmentation
from .models import build_models_from_meta
from .preprocess import (
    clahe3d,
    hist_match3d,
    n4_bias_correct,
    load_ibsr_reference_array_and_zooms,
    load_ibsr_reference_array_mask_and_zooms,
    load_nfbs_reference_array_and_zooms,
    ahe3d_sitk,
    robust_winsorize,
    percentile_linear_map_to_ref,
)
from scipy import ndimage as _ndi  # 3D morphology for quick ROI
from .metrics import compute_cm3_from_labels
from .viz import save_triptych, save_named_input
from .mask import postprocess_ss_mask, compute_head_roi3d
from .registration import rigid_register_to_reference
from .roi import bbox_from_mask, crop3d, pad_to_multiple_3d, unpad3d, paste_back_3d


@dataclass
class TimepointResult:
    name: str
    path: str
    brain_cm3: float
    gm_cm3: float
    wm_cm3: float
    csf_cm3: float
    brain_mm3: float
    gm_mm3: float
    wm_mm3: float
    csf_mm3: float


def _discover_patients(meta) -> List[str]:
    root_glob = cfg(meta, "longitudinal.patients_glob")
    if not root_glob:
        raise ValueError("Meta.longitudinal.patients_glob is required for --longitudinal")
    # Simple glob without deps
    base = os.path.dirname(root_glob)
    pat = os.path.basename(root_glob)
    if not os.path.isdir(base):
        raise FileNotFoundError(base)
    import fnmatch
    candidates = [os.path.join(base, d) for d in os.listdir(base) if os.path.isdir(os.path.join(base, d)) and fnmatch.fnmatch(d, pat)]
    return sorted(candidates)


def _list_timepoints(pdir: str, inputs_glob: str, order: str, order_regex: str | None = None) -> List[str]:
    import fnmatch
    files = [os.path.join(pdir, f) for f in os.listdir(pdir) if fnmatch.fnmatch(f, inputs_glob)]
    if not files:
        # fallback: any NIfTI
        files = [os.path.join(pdir, f) for f in os.listdir(pdir) if f.endswith((".nii", ".nii.gz"))]
    if order == "by_mtime":
        files.sort(key=lambda p: os.path.getmtime(p))
    else:
        if order_regex:
            import re
            rx = re.compile(order_regex)
            def keyfn(p):
                m = rx.search(os.path.basename(p))
                return int(m.group(1)) if m and m.groups() else os.path.basename(p)
            files.sort(key=keyfn)
        else:
            files.sort()  # by_name
    return files



def _write_csv(path: str, rows: List[Dict[str, float]], header: List[str]):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="") as f:
        # Ignore any keys not present in header to avoid failures when rows have extra provenance fields
        w = csv.DictWriter(f, fieldnames=header, extrasaction='ignore')
        w.writeheader()
        for r in rows:
            w.writerow(r)


def _deltas_consecutive(rows: List[Dict[str, float]], keys: List[str]) -> List[Dict[str, float]]:
    deltas = []
    prev = None
    for r in rows:
        if prev is None:
            d0 = {"name": r["name"]}
            for k in keys:
                d0[f"d_{k}"] = 0.0
                d0[f"d_{k}_pct"] = 0.0
            deltas.append(d0)
        else:
            d = {"name": r["name"]}
            for k in keys:
                dv = float(r[k] - prev[k])
                dp = float((dv / prev[k] * 100.0) if prev[k] else 0.0)
                d[f"d_{k}"] = dv
                d[f"d_{k}_pct"] = dp
            deltas.append(d)
        prev = r
    return deltas


def _deltas_vs_baseline(rows: List[Dict[str, float]], keys: List[str]) -> List[Dict[str, float]]:
    if not rows:
        return []
    base = rows[0]
    out = []
    for r in rows:
        d = {"name": r["name"]}
        for k in keys:
            dv = float(r[k] - base[k])
            dp = float((dv / base[k] * 100.0) if base[k] else 0.0)
            d[f"d_{k}"] = dv
            d[f"d_{k}_pct"] = dp
        out.append(d)
    return out


def run_longitudinal(meta) -> None:
    # Build a single timestamped output directory: MonDay_output_HHMMSS (e.g., Nov9_output_142530)
    base_out = cfg(meta, "output_dir", default=os.path.join(os.getcwd(), "outputs"))
    out_root = make_timestamped_output_dir(base_out)
    inputs_glob = cfg(meta, "longitudinal.inputs_glob", "*_ana.nii.gz")
    order = cfg(meta, "longitudinal.order", "by_name")
    order_regex = cfg(meta, "longitudinal.order_regex")
    resume = bool(cfg(meta, "longitudinal.resume", True))
    reg_enable = bool(cfg(meta, "registration.enable", False))
    reg_ref_mode = cfg(meta, "registration.reference", "first")
    # Manual crop config for AIIMS volumes (applied before orientation/registration)
    mc = cfg(meta, "preproc.manual_crop") or {}
    mc_apply = bool(mc.get("apply", False))
    mc_z = mc.get("z")
    mc_y = mc.get("y")
    mc_x = mc.get("x")
    # Enforce crop for longitudinal_data inputs by default (x:[120,370], y:[20,350])
    patients_glob = cfg(meta, "longitudinal.patients_glob") or ""
    patients_base = os.path.abspath(os.path.dirname(patients_glob)) if patients_glob else ""
    force_crop = "LongitudinalAnalysisAIIMS.pypi/longitudinal_data" in patients_base
    if force_crop:
        mc_apply = True if not mc.get("apply", False) else mc_apply
        # Apply [:,120:370,20:350] on array after (x,z,y) swap in old code;
        # Equivalent on raw (x,y,z): y:[20,350], z:[120,370]
        mc_y = mc_y if mc_y else [20, 350]
        mc_z = mc_z if mc_z else [120, 370]

    # Shared inference knobs
    psize_ss = int(cfg(meta, "infer.patch_size_ss", int(cfg(meta, "infer.patch_size", 256))))
    psize_seg = int(cfg(meta, "infer.patch_size_seg", int(cfg(meta, "infer.patch_size", 256))))
    overlap = int(cfg(meta, "infer.overlap", 32))
    use_gpu = False  # CPU-only enforced across package
    wave_ss = cfg(meta, "models.ss.wave", None)
    wave_seg = cfg(meta, "models.seg.wave", None)
    ss_cfg = cfg(meta, "models.ss") or {}
    seg_cfg = cfg(meta, "models.seg") or {}
    if not ss_cfg or not ss_cfg.get("checkpoint"):
        raise ValueError("models.ss.checkpoint is required in meta for longitudinal")
    if not seg_cfg or not seg_cfg.get("checkpoint"):
        raise ValueError("models.seg.checkpoint is required in meta for longitudinal")

    patients = _discover_patients(meta)
    for pdir in patients:
        pname = os.path.basename(pdir.rstrip(os.sep))
        out_dir = os.path.join(out_root, pname)
        os.makedirs(out_dir, exist_ok=True)
        tps = _list_timepoints(pdir, inputs_glob, order, order_regex)
        rows_cm3: List[Dict[str, float]] = []
        rows_mm3: List[Dict[str, float]] = []
        provenance_rows: List[Dict[str, str]] = []

        # Build models once per patient for throughput
        ss_model, seg_model = build_models_from_meta(meta)

        # Determine reference for registration and histogram matching
        ref_vol: np.ndarray | None = None
        ref_zooms: Tuple[float, float, float] | None = None
        if len(tps) > 0:
            # Build a baseline reference (first TP, cropped if enabled), used for registration and/or hist-match
            if mc_apply:
                xref4d, _, _, ref_zooms = load_raw_then_crop_then_ras(tps[0], crop={"z": mc_z, "y": mc_y, "x": mc_x})
            else:
                xref4d, _, _, ref_zooms = load_nifti_as_ras(tps[0])
            xr = xref4d[..., 0]
            clip_range = cfg(meta, "preproc.clip", [0.5, 99.5])
            if clip_range:
                lo = float(clip_range[0]); hi = float(clip_range[1])
                if not (0.0 <= lo < hi <= 100.0):
                    raise ValueError(f"invalid preproc.clip percentiles: {clip_range}")
                xr = percentile_clip(xr, lo, hi)
            xr = zscore_normalize(xr)
            ref_vol = xr.astype(np.float32)
        # IBSR reference (AHE-processed) + optional mask + zooms for matching/registration, if available
        _ibsr_ext = load_ibsr_reference_array_mask_and_zooms(meta)
        if _ibsr_ext:
            ibsr_ref, ibsr_ref_mask, ibsr_zooms = _ibsr_ext
        else:
            _ibsr = load_ibsr_reference_array_and_zooms(meta)
            ibsr_ref, ibsr_zooms = (_ibsr if _ibsr else (None, None))
            ibsr_ref_mask = None
        # Save a reference histogram PNG for auditing (once per patient)
        if ibsr_ref is not None:
            save_named_input(ibsr_ref, out_dir, prefix="ibsr", name="ref")

        eq_mode = (cfg(meta, "preproc.equalize", "none") or "none").lower()
        clahe_params = cfg(meta, "preproc.clahe", {}) or {}
        hm_ref_mode = cfg(meta, "preproc.hist_match_ref")
        # NFBS reference for pre-SS normalization (if chosen)
        _nfbs = load_nfbs_reference_array_and_zooms(meta)
        nfbs_ref, nfbs_zooms = (_nfbs if _nfbs else (None, None))

        for i_tp, tp_path in enumerate(tps):
            base = os.path.splitext(os.path.basename(tp_path))[0]
            tp_out_prefix = os.path.join(out_dir, base)
            # Resume skip
            if resume and os.path.exists(tp_out_prefix + "_seg.nii.gz"):
                # Load metrics if present
                mjson = tp_out_prefix + "_metrics.json"
                if os.path.exists(mjson):
                    with open(mjson, "r") as f:
                        m = json.load(f)
                    cm3 = m.get("segmentation_cm3", {})
                    row = {"name": base, "brain_cm3": cm3.get("brain_cm3", 0.0), "gm_cm3": cm3.get("gm_cm3", 0.0), "wm_cm3": cm3.get("wm_cm3", 0.0), "csf_cm3": cm3.get("csf_cm3", 0.0)}
                    rows_cm3.append(row)
                    continue

            if mc_apply:
                x4d, affine, header, zooms = load_raw_then_crop_then_ras(tp_path, crop={"z": mc_z, "y": mc_y, "x": mc_x})
            else:
                x4d, affine, header, zooms = load_nifti_as_ras(tp_path)
            orig_shape = x4d.shape[:3]
            x4d = maybe_centerpad_h_axis_to_cube(x4d)
            x = x4d[..., 0]
            # 3D rigid registration to IBSR grid when available (preferred) else to first TP if enabled.
            # Capture raw intensities for post-SS processing AFTER geometry is standardized (registration),
            # but BEFORE any intensity normalization/percentile clipping.
            if force_crop and ibsr_ref is not None and ibsr_zooms is not None:
                try:
                    x_reg, tx = rigid_register_to_reference(
                        x,
                        (float(zooms[0]), float(zooms[1]), float(zooms[2])),
                        ibsr_ref,
                        (float(ibsr_zooms[0]), float(ibsr_zooms[1]), float(ibsr_zooms[2])),
                    )
                    x = x_reg
                    zooms = ibsr_zooms
                    provenance_rows.append({"name": base, **{k: f"{v:.6f}" for k, v in tx.items()}, "reg_to": "IBSR"})
                except Exception as e:
                    provenance_rows.append({"name": base, "registration_error": f"{type(e).__name__}:{e}"})
            elif reg_enable and (i_tp > 0 or reg_ref_mode != "first") and ref_vol is not None and ref_zooms is not None:
                try:
                    x_reg, tx = rigid_register_to_reference(
                        x,
                        (float(zooms[0]), float(zooms[1]), float(zooms[2])),
                        ref_vol,
                        (float(ref_zooms[0]), float(ref_zooms[1]), float(ref_zooms[2])),
                    )
                    x = x_reg
                    zooms = ref_zooms
                    # record registration in provenance later
                    provenance_rows.append({"name": base, **{k: f"{v:.6f}" for k, v in tx.items()}})
                except Exception as e:
                    provenance_rows.append({"name": base, "registration_error": f"{type(e).__name__}:{e}"})
            # Preserve raw (pre-normalization) intensities (after any registration) for post-SS brain processing
            x_raw = x.copy()
            # Defer debug image/JSON saving to a single block later to avoid redundant try/excepts
            raw_snap = x_raw  # cropped+RAS pre-normalization
            ss_raw_snap = None
            seg_input_snap = None
            norm_debug = {}
            # Now apply optional percentile clip/z-score for the SS input path only (not affecting x_raw)
            clip_range = cfg(meta, "preproc.clip", [0.5, 99.5])
            # For AIIMS path (force_crop=True), keep SS input in raw units; do not percentile-clip here
            if clip_range and not force_crop:
                lo = float(clip_range[0]); hi = float(clip_range[1])
                if not (0.0 <= lo < hi <= 100.0):
                    raise ValueError(f"invalid preproc.clip percentiles: {clip_range}")
                x = percentile_clip(x, lo, hi)
            # Skip early z-score for AIIMS; normalize after HM
            if not force_crop and bool(cfg(meta, "preproc.zscore", True)):
                x = zscore_normalize(x)
            # Optional/forced pre-SS equalization (3D) to reduce domain shift
            aiims_force = force_crop  # longitudinal_data => AIIMS
            # For AIIMS path use simple ROI-based global rescale; otherwise respect meta
            eq_pre_mode = "roi_window" if aiims_force else (cfg(meta, "preproc.equalize_pre_ss", "none") or "none").lower()
            if eq_pre_mode == "clahe3d":
                x = clahe3d(x, mask=None, **({
                    "clip_limit": float(clahe_params.get("clip_limit", 0.01)),
                    "kernel_size": tuple(clahe_params.get("kernel_size", [8, 32, 32])),
                    "nbins": int(clahe_params.get("nbins", 256)),
                }))
            elif eq_pre_mode == "ahe3d":
                # N4 (global) -> AHE on full volume -> global robust window to [0,1]
                try:
                    x = n4_bias_correct(x, mask=None, shrink_factor=2, num_iterations=50)
                except Exception:
                    pass
                try:
                    x = ahe3d_sitk(x, alpha=1.0, beta=1.0)
                except Exception:
                    pass
                try:
                    vals = x[x != 0]
                    if vals.size < 10:
                        vals = x.ravel()
                    lo, hi = np.percentile(vals, [1.0, 99.0])
                    if hi > lo:
                        x = np.clip(x, lo, hi)
                        x = (x - lo) / (hi - lo)
                except Exception:
                    pass
                eq_pre_mode = "ahe3d_global"
            elif eq_pre_mode == "roi_window":
                # N4 (global) -> build head ROI -> rescale full volume with ROI percentiles to [0,1]
                try:
                    x = n4_bias_correct(x, mask=None, shrink_factor=2, num_iterations=50)
                except Exception:
                    pass
                try:
                    from skimage.filters import threshold_otsu as _otsu
                    t = float(_otsu(x))
                except Exception:
                    t = float(np.percentile(x, 60.0))
                roi = x > t
                D = x.shape[0]
                cut = int(0.25 * D)
                if cut > 0:
                    roi[:cut, :, :] = False
                roi = _ndi.binary_closing(roi, structure=np.ones((3, 3, 3)), iterations=2)
                try:
                    lbl, n = _ndi.label(roi)
                    if n > 0:
                        sizes = _ndi.sum(roi, lbl, index=range(1, n + 1))
                        roi = lbl == (1 + int(np.argmax(sizes)))
                except Exception:
                    pass
                try:
                    vals = x[roi]
                    lo, hi = np.percentile(vals, [1.0, 99.0])
                    if hi > lo:
                        x = np.clip(x, lo, hi)
                        x = (x - lo) / (hi - lo)
                except Exception:
                    pass
                eq_pre_mode = "roi_window"
            elif eq_pre_mode == "hist_match3d":
                try:
                    if aiims_force:
                        # AIIMS pre-SS: prefer NFBS anchor; fallback to IBSR if NFBS not provided.
                        ref_for_pre = nfbs_ref if nfbs_ref is not None else ibsr_ref
                        if ref_for_pre is None:
                            raise RuntimeError("Reference not found for pre-SS histogram matching. Set preproc.nfbs_ref (preferred) or preproc.ibsr_ref in meta.")
                        # N4 bias correction (no mask) to flatten large-scale bias
                        try:
                            x = n4_bias_correct(x, mask=None, shrink_factor=2, num_iterations=50)
                        except Exception:
                            pass
                        # Global 3D HM to AHE(NFBS/IBSR) reference so brain and background share the same domain
                        x = hist_match3d(x, ref=ref_for_pre, mask=None, ref_mask=None)
                        # Post-HM robust windowing over the whole volume to [0,1]
                        try:
                            vals = x[x != 0]
                            if vals.size < 10:
                                vals = x.ravel()
                            lo, hi = np.percentile(vals, [1.0, 99.0])
                            if hi > lo:
                                x = np.clip(x, lo, hi)
                                x = (x - lo) / (hi - lo)
                        except Exception:
                            pass
                        eq_pre_mode = "hist_match3d_ibsr"
                    else:
                        # Non-AIIMS path may still use meta-controlled HM
                        if ibsr_ref is not None:
                            x = hist_match3d(x, ref=ibsr_ref, mask=None)
                            eq_pre_mode = "hist_match3d_ibsr"
                        elif ref_vol is not None:
                            x = hist_match3d(x, ref=ref_vol, mask=None)
                except Exception as e:
                    provenance_rows.append({"name": base, "pre_ss_equalize_error": f"{type(e).__name__}:{e}"})
            x4d = x[..., None].astype(np.float32)
            # Inference stages (SS): pad to 256^3 to avoid tiling and preserve full FOV context
            from .roi import pad_to_shape_cube_3d  # local import
            x4d_ss, pads_ss = pad_to_shape_cube_3d(x4d, size=256)
            # Head ROI on the SS input grid to constrain postprocess growth
            head_roi_padded = compute_head_roi3d(x4d_ss[..., 0])
            ss_mask_padded, x4d_masked_padded = run_skull_strip(
                x4d_ss, ss_cfg, patch_size=psize_ss, overlap=overlap, use_gpu=use_gpu, wave=wave_ss, model=ss_model
            )
            # Post-process SS mask (keep largest component, fill holes, light closing, remove tiny islands)
            ss_post = cfg(meta, "preproc.ss_post", {}) or {}
            ss_min_size_frac = float(ss_post.get("min_size_frac", 0.01))
            ss_closing_iters = int(ss_post.get("closing_iters", 2))
            ss_ball_radius = int(ss_post.get("ball_radius", 3))
            ss_max_gap_vox = int(ss_post.get("max_gap_vox", 4))
            ss_volume_cap = float(ss_post.get("volume_cap_frac", 0.05))
            ss_mask_padded = postprocess_ss_mask(
                ss_mask_padded.astype(np.uint8),
                min_size_frac=ss_min_size_frac,
                closing_iters=ss_closing_iters,
                ball_radius=ss_ball_radius,
                max_gap_vox=ss_max_gap_vox,
                head_roi=head_roi_padded,
                volume_cap_frac=ss_volume_cap,
            )
            # Recompute masked SS input consistently with the cleaned mask
            x4d_masked_padded = x4d_ss.copy()
            x4d_masked_padded[..., 0] *= ss_mask_padded
            # Unpad SS outputs back to cropped shape
            ss_mask = unpad3d(ss_mask_padded, pads_ss)
            x4d_masked = unpad3d(x4d_masked_padded, pads_ss)

            # Post-SS: prepare skull-stripped brain for segmentation (no extra intensity scaling)
            if force_crop:
                # Use raw skull-stripped brain (pre-SS normalization), matched to the same 256^3 grid as SS
                xraw4d = x_raw[..., None].astype(np.float32)
                xraw4d_ss, pads_raw = pad_to_shape_cube_3d(xraw4d, size=256)
                x_post_padded = (xraw4d_ss[..., 0] * ss_mask_padded).astype(np.float32)
                x_post = unpad3d(x_post_padded, pads_raw)
                # Save skull-stripped raw brain (pre-N4/HM) snapshot/NIfTI for auditing (no try/except)
                save_named_input(x_post, out_dir, base, name="ssrawinput")
                # also save NIfTI to verify raw units in downstream tools
                save_nifti(x_post.astype(np.float32), affine, header, tp_out_prefix + "_ssraw.nii.gz")
                # N4 bias correction constrained by SS mask (non-fatal, but recorded)
                try:
                    x_post = n4_bias_correct(x_post, mask=ss_mask, shrink_factor=2, num_iterations=30)
                except Exception as e:
                    provenance_rows.append({"name": base, "n4_error": f"{type(e).__name__}:{e}"})
                # Scale skull-stripped brain to [0,255] using brain percentiles (float32; model will ZScoreNormalize)
                if bool(cfg(meta, "preproc.seg_scale_to_255", True)):
                    vals = x_post[ss_mask > 0]
                    if vals.size >= 10:
                        lo_p = float(cfg(meta, "preproc.seg_win_lo", 1.0))
                        hi_p = float(cfg(meta, "preproc.seg_win_hi", 99.0))
                        lo, hi = np.percentile(vals, [lo_p, hi_p])
                        if hi > lo:
                            x_post = np.clip(x_post, lo, hi)
                            x_post = (x_post - lo) / (hi - lo)
                            x_post *= 255.0
                        x_post[ss_mask <= 0] = 0.0
                x4d_masked = x_post[..., None].astype(np.float32)
                seg_input_snap = x4d_masked[..., 0]
            else:
                # Optional 3D equalization on masked brain for segmentation stage (non-AIIMS path)
                if eq_mode == "clahe3d":
                    x_eq = clahe3d(x4d_masked[..., 0], mask=ss_mask, **({
                        "clip_limit": float(clahe_params.get("clip_limit", 0.01)),
                        "kernel_size": tuple(clahe_params.get("kernel_size", [8, 32, 32])),
                        "nbins": int(clahe_params.get("nbins", 256)),
                    }))
                    x4d_masked = x_eq[..., None].astype(np.float32)
                elif eq_mode == "hist_match3d":
                    if ref_vol is None:
                        if hm_ref_mode == "first" or hm_ref_mode is None:
                            ref_vol = x4d_masked[..., 0].copy()
                        elif isinstance(hm_ref_mode, str) and os.path.exists(hm_ref_mode):
                            ref_x, _, _, _ = load_nifti_as_ras(hm_ref_mode)
                            ref_vol = ref_x[..., 0]
                    if ref_vol is not None:
                        x_eq = hist_match3d(x4d_masked[..., 0], ref=ref_vol, mask=ss_mask)
                        x4d_masked = x_eq[..., None].astype(np.float32)

            # Brain ROI crop and pad for segmentation throughput
            bbox = bbox_from_mask(ss_mask.astype(bool), margin=int(cfg(meta, "preproc.brain_bbox_margin", 8)))
            x_roi = crop3d(x4d_masked[..., 0], bbox)
            x_roi4d = x_roi[..., None].astype(np.float32)
            x_roi4d_pad, pads = pad_to_multiple_3d(x_roi4d, multiple=max(1, int(psize_seg)))
            _, seg_roi = run_segmentation(x_roi4d_pad, seg_cfg, patch_size=psize_seg, overlap=overlap, use_gpu=use_gpu, wave=wave_seg, model=seg_model)
            seg_roi = unpad3d(seg_roi, pads)
            seg_labels = paste_back_3d(x4d_masked[..., 0].shape, seg_roi, bbox, fill=0)

            # Removed anchor-based refine and extra mapping steps (model does its own normalization)

            # Save outputs and images
            save_nifti(ss_mask.astype(np.uint8), affine, header, tp_out_prefix + "_ssmask.nii.gz")
            save_nifti(seg_labels.astype(np.int16), affine, header, tp_out_prefix + "_seg.nii.gz")
            save_triptych(x4d[..., 0], ss_mask, seg_labels, out_dir, prefix=base)

            # Save debug artifacts (exact tensors seen by models)
            if raw_snap is not None:
                save_named_input(raw_snap, out_dir, base, name="rawinput")
            if seg_input_snap is not None:
                save_named_input(seg_input_snap, out_dir, base, name="seginput")

            # Metrics: brain_cm3 from SS mask; tissue cm3 from segmentation
            seg_cm3 = compute_cm3_from_labels(seg_labels, zooms)
            ss_cm3 = compute_cm3_from_labels(ss_mask.astype(np.int16), zooms)
            row_cm3 = {
                "name": base,
                "brain_cm3": ss_cm3.get("brain_cm3", 0.0),
                "gm_cm3": seg_cm3.get("gm_cm3", 0.0),
                "wm_cm3": seg_cm3.get("wm_cm3", 0.0),
                "csf_cm3": seg_cm3.get("csf_cm3", 0.0),
            }
            rows_cm3.append(row_cm3)
            row_mm3 = {
                "name": base,
                "brain_mm3": float(row_cm3["brain_cm3"] * 1000.0),
                "gm_mm3": float(row_cm3["gm_cm3"] * 1000.0),
                "wm_mm3": float(row_cm3["wm_cm3"] * 1000.0),
                "csf_mm3": float(row_cm3["csf_cm3"] * 1000.0),
            }
            rows_mm3.append(row_mm3)
            # save metrics json alongside tp outputs (both SS and seg)
            with open(tp_out_prefix + "_metrics.json", "w") as f:
                json.dump({"segmentation_cm3": seg_cm3, "skullstrip_cm3": ss_cm3}, f, indent=2)

            # provenance row
            provenance_rows.append({
                "name": base,
                "zoom_x": f"{zooms[0]:.6f}",
                "zoom_y": f"{zooms[1]:.6f}",
                "zoom_z": f"{zooms[2]:.6f}",
                "equalize": eq_mode,
                "clahe": json.dumps(clahe_params) if eq_mode == "clahe3d" or eq_pre_mode == "clahe3d" else "",
                "equalize_pre_ss": eq_pre_mode,
                "manual_crop_x": json.dumps(mc_x) if 'mc_x' in locals() and mc_x else "",
                "manual_crop_y": json.dumps(mc_y) if 'mc_y' in locals() and mc_y else "",
                "manual_crop_z": json.dumps(mc_z) if 'mc_z' in locals() and mc_z else "",
            })

        # Write per-patient metrics CSV/JSON
        metrics_csv = os.path.join(out_dir, "metrics_per_timepoint_cm3.csv")
        header_cm3 = ["name", "brain_cm3", "gm_cm3", "wm_cm3", "csf_cm3"]
        _write_csv(metrics_csv, rows_cm3, header_cm3)
        with open(os.path.join(out_dir, "metrics_per_timepoint_cm3.json"), "w") as f:
            json.dump(rows_cm3, f, indent=2)
        # mm3 variants
        metrics_mm3_csv = os.path.join(out_dir, "metrics_per_timepoint_mm3.csv")
        header_mm3 = ["name", "brain_mm3", "gm_mm3", "wm_mm3", "csf_mm3"]
        _write_csv(metrics_mm3_csv, rows_mm3, header_mm3)
        with open(os.path.join(out_dir, "metrics_per_timepoint_mm3.json"), "w") as f:
            json.dump(rows_mm3, f, indent=2)

        # Provenance CSV
        if provenance_rows:
            _write_csv(
                os.path.join(out_dir, "provenance.csv"),
                provenance_rows,
                [
                    "name",
                    "zoom_x", "zoom_y", "zoom_z",
                    "equalize", "equalize_pre_ss",
                    "clahe",
                    "manual_crop_x", "manual_crop_y", "manual_crop_z",
                    "reg_to", "registration_error", "pre_ss_equalize_error",
                ],
            )

        # Deltas (consecutive and vs baseline) in cm3
        keys_cm3 = ["brain_cm3", "gm_cm3", "wm_cm3", "csf_cm3"]
        deltas_cons = _deltas_consecutive(rows_cm3, keys_cm3)
        deltas_base = _deltas_vs_baseline(rows_cm3, keys_cm3)
        _write_csv(os.path.join(out_dir, "deltas_consecutive_cm3.csv"), deltas_cons, ["name"] + sum([[f"d_{k}", f"d_{k}_pct"] for k in keys_cm3], []))
        _write_csv(os.path.join(out_dir, "deltas_vs_baseline_cm3.csv"), deltas_base, ["name"] + sum([[f"d_{k}", f"d_{k}_pct"] for k in keys_cm3], []))
        with open(os.path.join(out_dir, "deltas_consecutive_cm3.json"), "w") as f:
            json.dump(deltas_cons, f, indent=2)
        with open(os.path.join(out_dir, "deltas_vs_baseline_cm3.json"), "w") as f:
            json.dump(deltas_base, f, indent=2)
        # mm3 deltas
        keys_mm3 = ["brain_mm3", "gm_mm3", "wm_mm3", "csf_mm3"]
        deltas_cons_mm3 = _deltas_consecutive(rows_mm3, keys_mm3)
        deltas_base_mm3 = _deltas_vs_baseline(rows_mm3, keys_mm3)
        _write_csv(os.path.join(out_dir, "deltas_consecutive_mm3.csv"), deltas_cons_mm3, ["name"] + sum([[f"d_{k}", f"d_{k}_pct"] for k in keys_mm3], []))
        _write_csv(os.path.join(out_dir, "deltas_vs_baseline_mm3.csv"), deltas_base_mm3, ["name"] + sum([[f"d_{k}", f"d_{k}_pct"] for k in keys_mm3], []))
        with open(os.path.join(out_dir, "deltas_consecutive_mm3.json"), "w") as f:
            json.dump(deltas_cons_mm3, f, indent=2)
        with open(os.path.join(out_dir, "deltas_vs_baseline_mm3.json"), "w") as f:
            json.dump(deltas_base_mm3, f, indent=2)

        # Simple summary plot
        try:
            import matplotlib
            matplotlib.use("Agg")
            import matplotlib.pyplot as plt
            xs = list(range(len(rows_cm3)))
            names = [r["name"] for r in rows_cm3]
            def _vals(key):
                return [float(r.get(key, 0.0)) for r in rows_cm3]
            plt.figure(figsize=(8, 4))
            plt.plot(xs, _vals("brain_cm3"), "-o", label="brain_cm3")
            plt.plot(xs, _vals("gm_cm3"), "-o", label="gm_cm3")
            plt.plot(xs, _vals("wm_cm3"), "-o", label="wm_cm3")
            plt.plot(xs, _vals("csf_cm3"), "-o", label="csf_cm3")
            plt.xticks(xs, names, rotation=45, ha="right")
            plt.legend(); plt.tight_layout()
            plt.savefig(os.path.join(out_dir, "longitudinal_summary.png"), bbox_inches="tight")
            plt.close()
        except Exception:
            pass
