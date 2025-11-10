""" MRILong: Longitudinal Analysis of Brain T1 MRI (3D) with Skull‑Strip and Tissue Segmentation

Minimal, meta-driven pipeline for:
- Skull stripping (binary mask)
- GM/WM/CSF segmentation (multi-class)
- Metrics (cm^3)
- Optional PNG snapshots and web viewer launch

This package reuses the existing MEDNet code without modifying it.
"""

# Enforce CPU-only execution regardless of host GPUs
import os as _os
_os.environ.setdefault("CUDA_VISIBLE_DEVICES", "-1")

__all__ = [
    "config",
    "io",
    "models",
    "tiling",
    "infer",
    "metrics",
    "viz",
    "webapp",
]



# Backward compatibility aliases
import sys as _sys
try:  # pragma: no cover - defensive
    from . import MEDNet as _mednet
    _sys.modules.setdefault("MEDNet", _mednet)
    # Old package name alias (allow external scripts still importing longaiims.*)
    _sys.modules.setdefault("longaiims", _sys.modules[__name__])
except Exception:  # pragma: no cover
    pass
