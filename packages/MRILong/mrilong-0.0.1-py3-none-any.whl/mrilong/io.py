from __future__ import annotations
import os
from typing import Tuple, Optional, Dict
import numpy as np
import nibabel as nib


def load_nifti_as_ras(path: str) -> Tuple[np.ndarray, np.ndarray, nib.nifti1.Nifti1Header, Tuple[float, float, float]]:
    """Load NIfTI, reorient to closest canonical (RAS), return data [D,H,W,1] float32.

    Returns: (data4d, affine, header, zooms)
    """
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    img = nib.load(path)
    img_c = nib.as_closest_canonical(img)
    data = img_c.get_fdata(dtype=np.float32)
    # Ensure 3D
    if data.ndim == 4:
        # take first channel if necessary
        data = data[..., 0]
    if data.ndim != 3:
        raise ValueError(f"Expected 3D volume, got shape {data.shape}")
    data4d = data[..., None]
    hdr = img_c.header.copy()
    zooms = tuple(float(z) for z in hdr.get_zooms()[:3])
    return data4d, img_c.affine, hdr, zooms


def save_nifti(data3d: np.ndarray, affine: np.ndarray, header: nib.nifti1.Nifti1Header, out_path: str) -> None:
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    # Preserve header dtype carefully
    hdr = header.copy()
    # Adjust dtype based on data type
    img = nib.Nifti1Image(data3d, affine, header=hdr)
    nib.save(img, out_path)


def zscore_normalize(x: np.ndarray, eps: float = 1e-6) -> np.ndarray:
    mu = np.mean(x)
    sigma = np.std(x)
    if sigma < eps:
        return x * 0.0
    return (x - mu) / (sigma + eps)


def percentile_clip(x: np.ndarray, lo: float = 0.5, hi: float = 99.5) -> np.ndarray:
    lo_v = np.percentile(x, lo)
    hi_v = np.percentile(x, hi)
    x = np.clip(x, lo_v, hi_v)
    # Rescale to 0-1
    if hi_v > lo_v:
        x = (x - lo_v) / (hi_v - lo_v)
    return x


def maybe_centerpad_h_axis_to_cube(vol: np.ndarray) -> np.ndarray:
    """If the volume is 256x128x256 (IBSR), zero-pad H by 64 on both sides to 256.
    vol shape: [D,H,W,1]
    """
    if vol.ndim != 4 or vol.shape[-1] != 1:
        raise ValueError("Expected [D,H,W,1]")
    D, H, W, C = vol.shape
    if (D, H, W) == (256, 128, 256):
        pad_cfg = ((0, 0), (64, 64), (0, 0), (0, 0))
        return np.pad(vol, pad_cfg, mode="constant")
    return vol


def load_raw_then_crop_then_ras(path: str,
                                crop: Optional[Dict[str, Optional[Tuple[int, int]]]] = None) -> Tuple[np.ndarray, np.ndarray, nib.nifti1.Nifti1Header, Tuple[float, float, float]]:
    """Load NIfTI in raw orientation, apply manual cropping slices, then canonicalize to RAS.

    crop: dict with optional keys 'z','y','x' each as (start, end) or None.
    Returns data4d [D,H,W,1] float32, affine, header, zooms.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    img = nib.load(path)
    nii = img
    if crop:
        # Note: NIfTI array order is (X, Y, Z). Apply slices as (sx, sy, sz).
        zc = crop.get('z') if 'z' in crop else None
        yc = crop.get('y') if 'y' in crop else None
        xc = crop.get('x') if 'x' in crop else None
        sz = slice(None) if (zc is None or zc == []) else slice(int(zc[0]), int(zc[1]))
        sy = slice(None) if (yc is None or yc == []) else slice(int(yc[0]), int(yc[1]))
        sx = slice(None) if (xc is None or xc == []) else slice(int(xc[0]), int(xc[1]))
        try:
            nii = img.slicer[sx, sy, sz]
        except Exception:
            # Fallback: crop array then wrap; affine will be approximate (no offset)
            arr = img.get_fdata().astype(np.float32)
            arr = arr[sx, sy, sz]
            nii = nib.Nifti1Image(arr, img.affine, header=img.header)
    # Canonicalize after manual crop
    nii_ras = nib.as_closest_canonical(nii)
    data = nii_ras.get_fdata(dtype=np.float32)
    if data.ndim == 4:
        data = data[..., 0]
    data4d = data[..., None]
    hdr = nii_ras.header.copy()
    zooms = tuple(float(z) for z in hdr.get_zooms()[:3])
    return data4d, nii_ras.affine, hdr, zooms

def load_label_as_ras(path: str) -> Tuple[np.ndarray, np.ndarray, nib.nifti1.Nifti1Header, Tuple[float, float, float]]:
    """Load label NIfTI as closest canonical (RAS); return int16 3D array.

    Returns: (labels3d, affine, header, zooms)
    """
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    img = nib.load(path)
    img_c = nib.as_closest_canonical(img)
    data = img_c.get_fdata()
    if data.ndim == 4:
        data = data[..., 0]
    labels = np.rint(data).astype(np.int16)
    hdr = img_c.header.copy()
    zooms = tuple(float(z) for z in hdr.get_zooms()[:3])
    return labels, img_c.affine, hdr, zooms
