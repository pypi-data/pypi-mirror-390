from __future__ import annotations
from typing import Dict
import numpy as np


def compute_cm3_from_labels(labels3d: np.ndarray, zooms_xyz: tuple[float, float, float]) -> Dict[str, float]:
    """Compute brain and tissue volumes in cm^3 from integer label map.

    TRI convention in this repo: 1=CSF, 2=GM, 3=WM (0=background).
    For skull-strip mask (2-class), treat >0 as brain.
    """
    vx_mm3 = float(zooms_xyz[0] * zooms_xyz[1] * zooms_xyz[2])
    mm3_to_cm3 = 1.0 / 1000.0

    uniq = np.unique(labels3d)
    vol = {}
    if np.any(uniq > 1):
        # 4-class TRI mapping: 1=CSF, 2=GM, 3=WM
        vol["csf_cm3"] = float(np.sum(labels3d == 1) * vx_mm3 * mm3_to_cm3)
        vol["gm_cm3"]  = float(np.sum(labels3d == 2) * vx_mm3 * mm3_to_cm3)
        vol["wm_cm3"]  = float(np.sum(labels3d == 3) * vx_mm3 * mm3_to_cm3)
        vol["brain_cm3"] = vol["gm_cm3"] + vol["wm_cm3"] + vol["csf_cm3"]
    else:
        # binary mask case
        vol["brain_cm3"] = float(np.sum(labels3d > 0) * vx_mm3 * mm3_to_cm3)
    return vol
