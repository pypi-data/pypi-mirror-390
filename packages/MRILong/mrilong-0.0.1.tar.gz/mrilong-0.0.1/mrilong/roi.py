from __future__ import annotations
from typing import Tuple, Optional
import numpy as np


def bbox_from_mask(mask3d: np.ndarray, margin: int = 8) -> Tuple[slice, slice, slice]:
    """Compute tight bbox around nonzero mask with margin; returns slices (z,y,x)."""
    assert mask3d.ndim == 3
    nz = np.nonzero(mask3d)
    if len(nz[0]) == 0:
        # Empty mask -> full volume
        D, H, W = mask3d.shape
        return (slice(0, D), slice(0, H), slice(0, W))
    zmin, zmax = np.min(nz[0]), np.max(nz[0])
    ymin, ymax = np.min(nz[1]), np.max(nz[1])
    xmin, xmax = np.min(nz[2]), np.max(nz[2])
    D, H, W = mask3d.shape
    z0 = max(0, zmin - margin); z1 = min(D, zmax + 1 + margin)
    y0 = max(0, ymin - margin); y1 = min(H, ymax + 1 + margin)
    x0 = max(0, xmin - margin); x1 = min(W, xmax + 1 + margin)
    return (slice(z0, z1), slice(y0, y1), slice(x0, x1))


def crop3d(vol: np.ndarray, bbox: Tuple[slice, slice, slice]) -> np.ndarray:
    return vol[bbox[0], bbox[1], bbox[2], ...]


def pad_to_multiple_3d(vol: np.ndarray, multiple: int) -> Tuple[np.ndarray, Tuple[Tuple[int, int], Tuple[int, int], Tuple[int, int]]]:
    """Zero-pad a 3D or 4D volume so D,H,W are multiples of 'multiple'. Returns padded vol and pad sizes per axis."""
    is4 = (vol.ndim == 4)
    if is4:
        D, H, W, C = vol.shape
    else:
        D, H, W = vol.shape
    def _pad_for(n):
        rem = n % multiple
        add = (multiple - rem) % multiple
        return (0, add)
    pd = _pad_for(D); ph = _pad_for(H); pw = _pad_for(W)
    pad_cfg = (pd, ph, pw, (0, 0)) if is4 else (pd, ph, pw)
    out = np.pad(vol, pad_cfg, mode="constant")
    return out, (pd, ph, pw)


def unpad3d(vol: np.ndarray, pads: Tuple[Tuple[int, int], Tuple[int, int], Tuple[int, int]]) -> np.ndarray:
    (pd, ph, pw) = pads
    D2 = vol.shape[0] - pd[1]
    H2 = vol.shape[1] - ph[1]
    W2 = vol.shape[2] - pw[1]
    return vol[:D2, :H2, :W2, ...]


def paste_back_3d(full_shape: Tuple[int, int, int], crop_labels: np.ndarray, bbox: Tuple[slice, slice, slice], fill: int = 0) -> np.ndarray:
    """Paste cropped labels back into a full-sized array."""
    out = np.full(full_shape, fill_value=fill, dtype=crop_labels.dtype)
    out[bbox[0], bbox[1], bbox[2]] = crop_labels
    return out


def pad_to_shape_cube_3d(vol: np.ndarray, size: int = 256) -> Tuple[np.ndarray, Tuple[Tuple[int, int], Tuple[int, int], Tuple[int, int]]]:
    """Zero-pad a 3D or 4D volume so D=H=W=size using symmetric padding (center-pad).

    Returns (padded_volume, pads), where pads are (pd, ph, pw) tuples of (before, after).
    """
    is4 = (vol.ndim == 4)
    if is4:
        D, H, W, C = vol.shape
    else:
        D, H, W = vol.shape
    def _sym_pad(n):
        add = max(0, size - n)
        before = add // 2
        after = add - before
        return (before, after)
    pd = _sym_pad(D); ph = _sym_pad(H); pw = _sym_pad(W)
    pad_cfg = (pd, ph, pw, (0, 0)) if is4 else (pd, ph, pw)
    out = np.pad(vol, pad_cfg, mode="constant")
    return out, (pd, ph, pw)
