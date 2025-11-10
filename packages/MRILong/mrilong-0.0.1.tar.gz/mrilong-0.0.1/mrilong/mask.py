from __future__ import annotations
import numpy as np
from scipy import ndimage as _ndi
try:
    from skimage.filters import threshold_otsu as _otsu
    _HAS_SKIMAGE = True
except Exception:
    _HAS_SKIMAGE = False


def _ball(radius: int) -> np.ndarray:
    r = int(max(1, radius))
    L = 2 * r + 1
    zz, yy, xx = np.mgrid[-r:r+1, -r:r+1, -r:r+1]
    return (xx*xx + yy*yy + zz*zz) <= (r * r)


def postprocess_ss_mask(mask3d: np.ndarray,
                        min_size_frac: float = 0.01,
                        closing_iters: int = 1,
                        ball_radius: int = 2,
                        max_gap_vox: int = 4,
                        head_roi: np.ndarray | None = None,
                        volume_cap_frac: float = 0.05) -> np.ndarray:
    """Clean a 3D skull-stripping mask.

    Steps (3D):
    - Keep largest component
    - Fill interior holes
    - Boundary-aware closing with a spherical struct (ball_radius), iterations
    - Distance-limited fill: fill only interior gaps with distance <= max_gap_vox
    - Remove tiny islands (< min_size_frac of brain)
    """
    m = (mask3d > 0)
    if m.sum() == 0:
        return mask3d.astype(np.uint8)
    pre = (mask3d > 0)
    pre_count = int(pre.sum())
    m = pre.copy()
    # Largest component
    lbl, n = _ndi.label(m)
    if n > 1:
        sizes = _ndi.sum(m, lbl, index=range(1, n + 1))
        keep = 1 + int(np.argmax(sizes))
        m = (lbl == keep)
    # Initial hole fill
    m = _ndi.binary_fill_holes(m)
    # Boundary-aware closing
    if closing_iters and closing_iters > 0:
        selem = _ball(ball_radius)
        m = _ndi.binary_closing(m, structure=selem, iterations=int(closing_iters))
    # Distance-limited interior gap fill
    filled = _ndi.binary_fill_holes(m)
    holes = np.logical_and(filled, ~m)
    if np.any(holes):
        dt = _ndi.distance_transform_edt(~m)
        small_holes = np.logical_and(holes, dt <= int(max_gap_vox))
        m = np.logical_or(m, small_holes)
    # Slice-wise hole filling (axial, coronal, sagittal) and union for thin slivers
    for axis in (0, 1, 2):
        m = _slicewise_fill_holes_union(m, axis=axis)
    # Constrain to head ROI if provided (but never remove original pre mask)
    if head_roi is not None and head_roi.shape == m.shape:
        roi = head_roi.astype(bool)
        # Slightly relax ROI to avoid cutting brain boundary
        roi = _ndi.binary_dilation(roi, structure=_ball(1))
        additions = np.logical_and(m, roi)
        m = np.logical_or(pre, additions)
    # Final clean: remove tiny islands
    lbl2, n2 = _ndi.label(m)
    if n2 > 1:
        sizes2 = _ndi.sum(m, lbl2, index=range(1, n2 + 1))
        max_size = float(np.max(sizes2))
        min_keep = max(1.0, float(min_size_frac) * max_size)
        keep_mask = np.zeros_like(m, dtype=bool)
        for i, s in enumerate(sizes2, start=1):
            if float(s) >= min_keep:
                keep_mask |= (lbl2 == i)
        m = keep_mask
    # Volume growth cap
    post_count = int(m.sum())
    if pre_count > 0 and post_count > int((1.0 + float(volume_cap_frac)) * pre_count):
        # Restrict additions to a dilation shell of the original mask
        shell = _ndi.binary_dilation(pre, structure=_ball(max_gap_vox))
        additions = np.logical_and(m, shell)
        m = np.logical_or(pre, additions)
    # Final interior hole fill to ensure no new holes introduced
    m = _ndi.binary_fill_holes(m)
    return m.astype(np.uint8)


def _slicewise_fill_holes_union(m: np.ndarray, axis: int = 0) -> np.ndarray:
    """Fill 2D holes per-slice along given axis and union with m (conservative)."""
    m = m.astype(bool, copy=False)
    out = m.copy()
    if axis == 0:
        for i in range(m.shape[0]):
            sl = m[i, :, :]
            out[i, :, :] = np.logical_or(out[i, :, :], _ndi.binary_fill_holes(sl))
    elif axis == 1:
        for j in range(m.shape[1]):
            sl = m[:, j, :]
            out[:, j, :] = np.logical_or(out[:, j, :], _ndi.binary_fill_holes(sl))
    else:
        for k in range(m.shape[2]):
            sl = m[:, :, k]
            out[:, :, k] = np.logical_or(out[:, :, k], _ndi.binary_fill_holes(sl))
    return out


def compute_head_roi3d(vol3d: np.ndarray) -> np.ndarray:
    """Estimate a head ROI from a 3D anatomical volume (dataset‑agnostic).

    Uses Otsu (or percentile fallback), keeps largest component, closes small gaps.
    """
    x = np.asarray(vol3d)
    if x.size == 0:
        return np.zeros_like(x, dtype=np.uint8)
    try:
        t = float(_otsu(x)) if _HAS_SKIMAGE else float(np.percentile(x, 60.0))
    except Exception:
        t = float(np.percentile(x, 60.0))
    roi = x > t
    roi = _ndi.binary_closing(roi, structure=_ball(2), iterations=1)
    lbl, n = _ndi.label(roi)
    if n > 1:
        sizes = _ndi.sum(roi, lbl, index=range(1, n + 1))
        keep = 1 + int(np.argmax(sizes))
        roi = (lbl == keep)
    return roi.astype(np.uint8)
