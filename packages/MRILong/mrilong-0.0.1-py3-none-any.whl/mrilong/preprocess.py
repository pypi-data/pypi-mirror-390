from __future__ import annotations
from typing import Optional, Sequence, Tuple
import os
import glob
import numpy as np

try:
    import SimpleITK as sitk  # type: ignore
    _HAS_SITK = True
except Exception:
    _HAS_SITK = False

try:
    from skimage.exposure import equalize_adapthist as _clahe, match_histograms as _match_hist  # type: ignore
    _HAS_SKIMAGE = True
except Exception:
    _HAS_SKIMAGE = False

try:
    import nibabel as nib  # type: ignore
    _HAS_NIB = True
except Exception:
    _HAS_NIB = False


def clahe3d(x: np.ndarray, mask: Optional[np.ndarray] = None, *, clip_limit: float = 0.01, kernel_size: Optional[Sequence[int]] = None, nbins: int = 256) -> np.ndarray:
    """3D CLAHE on volume x; if mask given, apply and return x with only masked voxels equalized.

    x: float32 volume [D,H,W]
    """
    if not _HAS_SKIMAGE:
        return x
    if kernel_size is None:
        kernel_size = (8, 32, 32)
    # skimage equalize_adapthist expects values in [0,1]
    x_min, x_max = float(np.min(x)), float(np.max(x))
    xr = (x - x_min) / (x_max - x_min + 1e-6)
    xe = _clahe(xr, kernel_size=tuple(kernel_size), clip_limit=float(clip_limit), nbins=int(nbins))
    # Rescale back to original scale
    xe = xe * (x_max - x_min) + x_min
    if mask is None:
        return xe.astype(x.dtype, copy=False)
    out = x.copy()
    out[mask > 0.5] = xe[mask > 0.5]
    return out.astype(x.dtype, copy=False)


def hist_match3d(x: np.ndarray, ref: np.ndarray, mask: Optional[np.ndarray] = None, ref_mask: Optional[np.ndarray] = None) -> np.ndarray:
    """3D histogram matching of x to ref.

    - If no masks, prefer SimpleITK's HistogramMatching (fast, robust).
    - If masks provided, use scikit-image match_histograms on the masked vectors and assign back.
    """
    if mask is None and ref_mask is None and _HAS_SITK:
        try:
            mov = sitk.GetImageFromArray(x.astype(np.float32))
            ref_img = sitk.GetImageFromArray(ref.astype(np.float32))
            hm = sitk.HistogramMatchingImageFilter()
            hm.SetNumberOfHistogramLevels(2048)
            hm.SetNumberOfMatchPoints(100)
            hm.SetThresholdAtMeanIntensity(True)
            out = hm.Execute(mov, ref_img)
            return sitk.GetArrayFromImage(out).astype(x.dtype, copy=False)
        except Exception:
            pass
    if not _HAS_SKIMAGE:
        # Fallback: if scikit-image not available, try SimpleITK global HM even if masks were requested
        if _HAS_SITK:
            try:
                mov = sitk.GetImageFromArray(x.astype(np.float32))
                ref_img = sitk.GetImageFromArray(ref.astype(np.float32))
                hm = sitk.HistogramMatchingImageFilter()
                hm.SetNumberOfHistogramLevels(2048)
                hm.SetNumberOfMatchPoints(100)
                hm.SetThresholdAtMeanIntensity(True)
                out = hm.Execute(mov, ref_img)
                return sitk.GetArrayFromImage(out).astype(x.dtype, copy=False)
            except Exception:
                pass
        return x
    if mask is None and ref_mask is None:
        return _match_hist(x, ref).astype(x.dtype, copy=False)
    # Mask-aware path: match masked moving voxels to masked reference voxels (different shapes ok)
    m = (mask > 0.5) if mask is not None else np.ones_like(x, dtype=bool)
    if ref_mask is not None:
        rsel = ref[ref_mask > 0.5]
    else:
        rsel = ref.ravel()
    xsel = x[m]
    xmatched = _match_hist(xsel, rsel).astype(x.dtype, copy=False)
    out = x.copy()
    out[m] = xmatched
    return out


def n4_bias_correct(x: np.ndarray, mask: Optional[np.ndarray] = None, shrink_factor: int = 2, num_iterations: int = 50) -> np.ndarray:
    """Apply N4 bias field correction (SimpleITK) on 3D volume; returns float32 array.
    If mask provided, constrains correction to head/brain region.
    """
    if not _HAS_SITK:
        return x
    try:
        img = sitk.GetImageFromArray(x.astype(np.float32))
        if mask is not None:
            m = sitk.GetImageFromArray((mask.astype(np.uint8)))
        else:
            m = sitk.OtsuThreshold(img, 0, 1)
        corrector = sitk.N4BiasFieldCorrectionImageFilter()
        corrector.SetMaximumNumberOfIterations([num_iterations])
        corrector.SetShrinkFactor(shrink_factor)
        out = corrector.Execute(img, m)
        return sitk.GetArrayFromImage(out).astype(np.float32, copy=False)
    except Exception:
        return x


def ahe3d_sitk(x: np.ndarray, alpha: float = 1.0, beta: float = 1.0) -> np.ndarray:
    """Adaptive Histogram Equalization using SimpleITK to mirror 2D pipeline; returns float32 numpy array."""
    if not _HAS_SITK:
        return x
    img = sitk.GetImageFromArray(x.astype(np.float32))
    ahe = sitk.AdaptiveHistogramEqualizationImageFilter()
    ahe.SetAlpha(float(alpha))
    ahe.SetBeta(float(beta))
    out = ahe.Execute(img)
    return sitk.GetArrayFromImage(out).astype(np.float32, copy=False)


def load_ibsr_reference_from_env_or_meta(meta) -> Optional[np.ndarray]:
    """Load an IBSR reference volume (RAS), apply AHE to serve as HM anchor; returns 3D numpy or None."""
    # Meta-provided ref path takes precedence
    try:
        from .config import get as cfg  # local import to avoid cycles
    except Exception:
        cfg = lambda m, k, d=None: d  # type: ignore

    ref_path = None
    try:
        ref_path = cfg(meta, "preproc.ibsr_ref")
    except Exception:
        ref_path = None

    # Env IBSR_ROOT fallback
    if not ref_path:
        root = os.environ.get("IBSR_ROOT")
        if root and os.path.isdir(root):
            # Prefer a canonical subject; else any *_ana.nii.gz
            cand = os.path.join(root, "IBSR_01", "IBSR_01_ana.nii.gz")
            if os.path.exists(cand):
                ref_path = cand
            else:
                hits = glob.glob(os.path.join(root, "IBSR_*", "IBSR_*_ana.nii.gz"))
                ref_path = hits[0] if hits else None
    # Hard fallback: None
    if not ref_path or not _HAS_NIB:
        return None
    try:
        img = nib.load(ref_path)
        img = nib.as_closest_canonical(img)
        arr = img.get_fdata().astype(np.float32)
        if arr.ndim == 4:
            arr = arr[..., 0]
        # Apply AHE to mirror prior pipeline
        arr = ahe3d_sitk(arr, alpha=1.0, beta=1.0)
        return arr
    except Exception:
        return None


def load_ibsr_reference_array_and_zooms(meta) -> Optional[tuple[np.ndarray, tuple[float, float, float]]]:
    """Load IBSR ref array (AHE-processed) and its zooms (spacing)."""
    if not _HAS_NIB:
        return None
    try:
        # Reuse path resolution from helper above
        from .config import get as cfg
        ref_path = cfg(meta, "preproc.ibsr_ref")
        if not ref_path:
            root = os.environ.get("IBSR_ROOT")
            if root and os.path.isdir(root):
                cand = os.path.join(root, "IBSR_01", "IBSR_01_ana.nii.gz")
                if os.path.exists(cand):
                    ref_path = cand
                else:
                    hits = glob.glob(os.path.join(root, "IBSR_*", "IBSR_*_ana.nii.gz"))
                    ref_path = hits[0] if hits else None
        if not ref_path:
            return None
        img = nib.load(ref_path)
        img = nib.as_closest_canonical(img)
        arr = img.get_fdata().astype(np.float32)
        if arr.ndim == 4:
            arr = arr[..., 0]
        arr = ahe3d_sitk(arr, alpha=1.0, beta=1.0)
        zooms = tuple(float(z) for z in img.header.get_zooms()[:3])
        return arr, zooms
    except Exception:
        return None


def load_ibsr_reference_array_mask_and_zooms(meta) -> Optional[tuple[np.ndarray, Optional[np.ndarray], tuple[float, float, float]]]:
    """Load IBSR ref array (AHE-processed), an optional reference brain mask, and zooms.

    Meta keys:
      - preproc.ibsr_ref: path to IBSR reference anatomical NIfTI
      - preproc.ibsr_ref_mask (optional): path to a brain mask in the same space
    """
    if not _HAS_NIB:
        return None
    try:
        from .config import get as cfg
        ref_path = cfg(meta, "preproc.ibsr_ref")
        mask_path = cfg(meta, "preproc.ibsr_ref_mask")
        if not ref_path:
            root = os.environ.get("IBSR_ROOT")
            if root and os.path.isdir(root):
                cand = os.path.join(root, "IBSR_01", "IBSR_01_ana.nii.gz")
                if os.path.exists(cand):
                    ref_path = cand
                else:
                    hits = glob.glob(os.path.join(root, "IBSR_*", "IBSR_*_ana.nii.gz"))
                    ref_path = hits[0] if hits else None
        if not ref_path:
            return None
        img = nib.load(ref_path)
        img = nib.as_closest_canonical(img)
        arr = img.get_fdata().astype(np.float32)
        if arr.ndim == 4:
            arr = arr[..., 0]
        arr = ahe3d_sitk(arr, alpha=1.0, beta=1.0)
        zooms = tuple(float(z) for z in img.header.get_zooms()[:3])
        ref_mask = None
        if mask_path and os.path.exists(mask_path):
            mimg = nib.load(mask_path)
            mimg = nib.as_closest_canonical(mimg)
            m = mimg.get_fdata()
            if m.ndim == 4:
                m = m[..., 0]
            # Consider any nonzero as brain
            ref_mask = (m > 0).astype(np.uint8)
        return arr, ref_mask, zooms
    except Exception:
        return None


def load_nfbs_reference_array_and_zooms(meta) -> Optional[tuple[np.ndarray, tuple[float, float, float]]]:
    """Load NFBS reference array (optionally AHE-processed) and zooms.

    Meta key: preproc.nfbs_ref
    """
    if not _HAS_NIB:
        return None
    try:
        from .config import get as cfg
        ref_path = cfg(meta, "preproc.nfbs_ref")
        if not ref_path or not os.path.exists(ref_path):
            return None
        img = nib.load(ref_path)
        img = nib.as_closest_canonical(img)
        arr = img.get_fdata().astype(np.float32)
        if arr.ndim == 4:
            arr = arr[..., 0]
        # Keep same AHE anchor behavior for consistency
        arr = ahe3d_sitk(arr, alpha=1.0, beta=1.0)
        zooms = tuple(float(z) for z in img.header.get_zooms()[:3])
        return arr, zooms
    except Exception:
        return None


def robust_winsorize(x: np.ndarray, mask: Optional[np.ndarray] = None, lo: float = 1.0, hi: float = 99.0) -> Tuple[np.ndarray, float, float]:
    """Clamp x to [lo,hi] percentiles computed over mask (or all voxels if mask None).

    Returns (winsorized_x, p_lo, p_hi).
    """
    try:
        if mask is not None:
            vals = x[mask > 0]
            if vals.size < 10:
                vals = x.ravel()
        else:
            vals = x.ravel()
        plo, phi = np.percentile(vals, [float(lo), float(hi)])
        if phi > plo:
            xo = np.clip(x, plo, phi)
            return xo, float(plo), float(phi)
        return x, float(plo), float(phi)
    except Exception:
        return x, float(np.min(x)), float(np.max(x))


def percentile_linear_map_to_ref(x: np.ndarray,
                                 mask: Optional[np.ndarray],
                                 ref: np.ndarray,
                                 ref_mask: Optional[np.ndarray],
                                 lo: float = 1.0,
                                 hi: float = 99.0) -> Tuple[np.ndarray, Tuple[float, float, float, float]]:
    """Linearly map x's [lo,hi] masked percentiles to ref's [lo,hi] masked percentiles.

    Returns (mapped_x, (x_lo, x_hi, r_lo, r_hi)).
    """
    try:
        xv = x[mask > 0] if mask is not None else x.ravel()
        rv = ref[ref_mask > 0] if ref_mask is not None else ref.ravel()
        xlo, xhi = np.percentile(xv, [float(lo), float(hi)])
        rlo, rhi = np.percentile(rv, [float(lo), float(hi)])
        if (xhi > xlo) and (rhi > rlo):
            y = (x - xlo) / (xhi - xlo)
            y = y * (rhi - rlo) + rlo
            return y.astype(np.float32, copy=False), (float(xlo), float(xhi), float(rlo), float(rhi))
        return x, (float(xlo), float(xhi), float(rlo), float(rhi))
    except Exception:
        return x, (float(np.min(x)), float(np.max(x)), float(np.min(ref)), float(np.max(ref)))


## Removed experimental intensity mapping helpers (not used in current pipeline)
