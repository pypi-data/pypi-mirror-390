from __future__ import annotations
import argparse
import json
import os
from typing import Optional
import numpy as np

from .config import load_meta, get as cfg
from .paths import make_timestamped_output_dir
from .io import load_nifti_as_ras, save_nifti, zscore_normalize, percentile_clip, maybe_centerpad_h_axis_to_cube, load_label_as_ras
from .infer import run_skull_strip, run_segmentation
from .mask import postprocess_ss_mask, compute_head_roi3d
from .models import build_models_from_meta
from .metrics import compute_cm3_from_labels
from .viz import save_triptych
from .webapp import launch_viewer_if_requested


def _resolve_input_path(meta) -> str:
    path = cfg(meta, "phase1_test_data_optional.input")
    if not path:
        raise ValueError("Meta must include 'phase1_test_data_optional.input' pointing to a NIfTI file for Phase 1.")
    if os.path.isdir(path):
        files = [fn for fn in sorted(os.listdir(path)) if fn.endswith(".nii") or fn.endswith(".nii.gz")]
        if not files:
            raise ValueError(f"No NIfTI files found in directory: {path}")
        # If skull stripping stage is enabled, prefer raw anatomical (_ana) over already stripped
        if cfg(meta, "models.ss"):
            for fn in files:
                name = fn.lower()
                if name.endswith("_ana.nii.gz") or name.endswith("_ana.nii"):
                    return os.path.join(path, fn)
        # Fallback to first
        return os.path.join(path, files[0])
    return path


def main(argv: Optional[list[str]] = None) -> None:
    p = argparse.ArgumentParser(description="LongitudinalAnalysisAIIMS – Phase 1/2: inference and longitudinal analysis")
    p.add_argument("--meta", required=True, help="Path to meta JSON/YAML config")
    p.add_argument("--webapp", action="store_true", help="Launch web viewer (if available)")
    p.add_argument("--webview", action="store_true", help="Alias for --webapp")
    p.add_argument("--longitudinal", action="store_true", help="Enable longitudinal analysis over patient folders")
    args = p.parse_args(argv)

    meta = load_meta(args.meta)
    # Apply environment overrides from meta (for model factory sizing knobs)
    env_map = cfg(meta, "env", {}) or {}
    for k, v in env_map.items():
        os.environ[str(k)] = str(v)
    if args.longitudinal:
        # Defer to longitudinal orchestrator; keep Phase 1 untouched otherwise
        from .longitudinal import run_longitudinal
        run_longitudinal(meta)
        return

    # Phase 1 (single-volume): build timestamped output dir once here
    out_dir = cfg(meta, "output_dir", default=os.path.join(os.getcwd(), "outputs"))
    out_dir = make_timestamped_output_dir(out_dir)

    # Preproc knobs
    psize = int(cfg(meta, "infer.patch_size", 256))
    psize_ss = int(cfg(meta, "infer.patch_size_ss", psize))
    psize_seg = int(cfg(meta, "infer.patch_size_seg", psize))
    overlap = int(cfg(meta, "infer.overlap", 32))
    use_gpu = bool(cfg(meta, "infer.use_gpu", False))
    do_zscore = bool(cfg(meta, "preproc.zscore", True))
    do_equalize = bool(cfg(meta, "preproc.equalize", False))  # reserved for Phase 2
    clip_range = cfg(meta, "preproc.clip", [0.5, 99.5])
    wave_ss = cfg(meta, "models.ss.wave", None)
    wave_seg = cfg(meta, "models.seg.wave", None)

    inp_path = _resolve_input_path(meta)
    # Critical safety: if skull stripping is enabled and the input appears to be already stripped, try to switch to raw _ana
    if cfg(meta, "models.ss"):
        base = os.path.basename(inp_path).lower()
        if "ana_strip" in base:
            cand = inp_path.replace("_ana_strip", "_ana")
            if os.path.exists(cand):
                print(f"[fix] Using raw anatomical for SS: {cand}")
                inp_path = cand
            else:
                raise ValueError(f"Skull-stripping expects raw '_ana' input, but got '{inp_path}'. Please set phase1_test_data_optional.input to the raw anatomical file.")
    x4d, affine, header, zooms = load_nifti_as_ras(inp_path)
    orig_shape = x4d.shape[:3]
    # Optional IBSR center-pad to cube
    x4d = maybe_centerpad_h_axis_to_cube(x4d)

    # Intensity preproc
    x = x4d[..., 0]
    if clip_range:
        try:
            x = percentile_clip(x, float(clip_range[0]), float(clip_range[1]))
        except Exception:
            x = percentile_clip(x)
    if do_zscore:
        x = zscore_normalize(x)
    # Placeholder for equalization (Phase 2), keep identity for now
    if do_equalize:
        pass
    x4d = x[..., None].astype(np.float32)

    # Stage 1: Skull stripping
    ss_cfg = cfg(meta, "models.ss") or {}
    if not ss_cfg or not ss_cfg.get("checkpoint"):
        raise ValueError("models.ss.checkpoint is required in meta")
    # Build models once and reuse for both stages
    ss_model, seg_model = build_models_from_meta(meta)
    ss_mask, x4d_masked = run_skull_strip(x4d, ss_cfg, patch_size=psize_ss, overlap=overlap, use_gpu=use_gpu, wave=wave_ss, model=ss_model)
    # Meta-parametrized SS mask cleanup with head ROI constraint, defaults matching longitudinal path
    ss_post = cfg(meta, "preproc.ss_post", {}) or {}
    ss_min_size_frac = float(ss_post.get("min_size_frac", 0.01))
    ss_closing_iters = int(ss_post.get("closing_iters", 2))
    ss_ball_radius = int(ss_post.get("ball_radius", 3))
    ss_max_gap_vox = int(ss_post.get("max_gap_vox", 4))
    ss_volume_cap = float(ss_post.get("volume_cap_frac", 0.05))
    head_roi = compute_head_roi3d(x4d[..., 0])
    ss_mask = postprocess_ss_mask(
        ss_mask.astype(np.uint8),
        min_size_frac=ss_min_size_frac,
        closing_iters=ss_closing_iters,
        ball_radius=ss_ball_radius,
        max_gap_vox=ss_max_gap_vox,
        head_roi=head_roi,
        volume_cap_frac=ss_volume_cap,
    )
    x4d_masked = x4d.copy(); x4d_masked[..., 0] *= ss_mask

    # Stage 2: GM/WM/CSF segmentation
    seg_cfg = cfg(meta, "models.seg") or {}
    if not seg_cfg or not seg_cfg.get("checkpoint"):
        raise ValueError("models.seg.checkpoint is required in meta")
    probs4d, seg_labels = run_segmentation(x4d_masked, seg_cfg, patch_size=psize_seg, overlap=overlap, use_gpu=use_gpu, wave=wave_seg, model=seg_model)

    # If we center-padded H from 128->256, crop predictions back to original shape for saving
    def _maybe_crop_to_orig(arr3d):
        if arr3d.shape[:3] == (256, 256, 256) and orig_shape == (256, 128, 256):
            # crop center 128 along H axis
            return arr3d[:, 64:64+128, :]
        return arr3d

    ss_mask = _maybe_crop_to_orig(ss_mask)
    seg_labels = _maybe_crop_to_orig(seg_labels)

    # Save outputs
    base = os.path.splitext(os.path.basename(inp_path))[0]
    save_nifti(ss_mask.astype(np.uint8), affine, header, os.path.join(out_dir, f"{base}_ssmask.nii.gz"))
    save_nifti(seg_labels.astype(np.int16), affine, header, os.path.join(out_dir, f"{base}_seg.nii.gz"))

    # PNGs
    # Optional ground truths
    gt_mask_path = cfg(meta, "phase1_test_data_optional.gt_mask")
    gt_seg_path = cfg(meta, "phase1_test_data_optional.gt_seg")
    gt_mask = None
    gt_seg = None
    try:
        if gt_mask_path:
            gt_mask, _, _, _ = load_label_as_ras(gt_mask_path)
        if gt_seg_path:
            gt_seg, _, _, _ = load_label_as_ras(gt_seg_path)
    except Exception as e:
        print("Warning: failed to load provided ground truths:", type(e).__name__, e)

    save_triptych(x4d[..., 0], ss_mask, seg_labels, out_dir, prefix=base, gt_mask3d=gt_mask, gt_labels3d=gt_seg)

    # Metrics
    vols = compute_cm3_from_labels(seg_labels, zooms)
    # Also compute brain volume from SS mask for reference
    vols_ss = compute_cm3_from_labels(ss_mask.astype(np.int16), zooms)
    metrics = {"input": inp_path, "segmentation_cm3": vols, "skullstrip_cm3": vols_ss}
    with open(os.path.join(out_dir, f"{base}_metrics.json"), "w") as f:
        json.dump(metrics, f, indent=2)

    # Optional web viewer (best effort)
    if args.webapp or args.webview:
        try:
            url = launch_viewer_if_requested(x4d[..., 0], seg_labels, None, figs_dir=out_dir, open_browser=False)
            if url:
                print(f"Web viewer available at: {url}")
        except Exception as e:
            print("Warning: failed to launch web viewer:", type(e).__name__, e)


if __name__ == "__main__":
    main()
