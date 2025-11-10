from __future__ import annotations
from typing import Dict, Tuple, Optional
import numpy as np
import os as _os
# Hardcode CPU-only by hiding all CUDA devices for TensorFlow
_os.environ.setdefault("CUDA_VISIBLE_DEVICES", "-1")
import tensorflow as tf

from .models import build_model, load_weights_best_effort
from .tiling import sliding_window_predict


def _choose_device(use_gpu: bool) -> str:
    # Force CPU regardless of meta flag
    return "/CPU:0"


def run_skull_strip(x4d: np.ndarray,
                    ss_cfg: Dict,
                    patch_size: int,
                    overlap: int,
                    use_gpu: bool,
                    wave: Optional[str] = None,
                    model=None) -> Tuple[np.ndarray, np.ndarray]:
    """Run skull stripping and return (mask3d, x4d_masked)."""
    device = _choose_device(use_gpu)
    with tf.device(device):
        n_classes = int(ss_cfg.get("n_classes", 2))
        loss = ss_cfg.get("loss", "focal")
        ckpt = ss_cfg["checkpoint"]
        model_type = ss_cfg.get("type", "uwavevitnet")
        class_weights = [0.1] * n_classes if "focal" in (loss or "").lower() else None
        if model is None:
            model = build_model(model_type, input_size=patch_size, n_classes=n_classes, loss=loss, class_weights=class_weights, wave=wave, compile_flag=True)
            load_weights_best_effort(model, ckpt)

        if patch_size == 256 and x4d.shape[:3] == (256, 256, 256):
            x_tf = tf.convert_to_tensor(x4d[None, ...])
            pred = model.predict(x_tf, verbose=0)[0]
        else:
            pred = sliding_window_predict(model, x4d, patch_size, overlap, n_classes, batch_size=1)

        labels = np.argmax(pred, axis=-1).astype(np.int16)
        mask = (labels > 0).astype(np.float32)
        x_masked = x4d.copy()
        x_masked[..., 0] *= mask
        return mask.astype(np.uint8), x_masked


def run_segmentation(x4d_masked: np.ndarray,
                     seg_cfg: Dict,
                     patch_size: int,
                     overlap: int,
                     use_gpu: bool,
                     wave: Optional[str] = None,
                     model=None) -> Tuple[np.ndarray, np.ndarray]:
    """Run GM/WM/CSF segmentation and return (probs4d, labels3d)."""
    device = _choose_device(use_gpu)
    with tf.device(device):
        n_classes = int(seg_cfg.get("n_classes", 4))
        loss = seg_cfg.get("loss", "focal")
        ckpt = seg_cfg["checkpoint"]
        model_type = seg_cfg.get("type", "ufdstvitnet")
        class_weights = [0.1] * n_classes if "focal" in (loss or "").lower() else None
        if model is None:
            model = build_model(model_type, input_size=patch_size, n_classes=n_classes, loss=loss, class_weights=class_weights, wave=wave, compile_flag=True)
            load_weights_best_effort(model, ckpt)

        if patch_size == 256 and x4d_masked.shape[:3] == (256, 256, 256):
            x_tf = tf.convert_to_tensor(x4d_masked[None, ...])
            probs = model.predict(x_tf, verbose=0)[0]
        else:
            probs = sliding_window_predict(model, x4d_masked, patch_size, overlap, n_classes, batch_size=1)

        labels = np.argmax(probs, axis=-1).astype(np.int16)
        return probs, labels
