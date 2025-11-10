from __future__ import annotations
import os
import sys
from typing import Optional, Any, Tuple


def _ensure_mednet_path() -> None:
    """Insert a vendored MEDNet path relative to this repo (standalone).

    Tries, in order:
      - <repo>/LongitudinalAnalysisAIIMS.pypi/MEDNet.pypi
      - <repo>/LongitudinalAnalysisAIIMS.pypi/MEDNet
      - <repo>/LongitudinalAnalysisAIIMS.pypi/vendor/MEDNet.pypi
    """
    here = os.path.abspath(os.path.dirname(__file__))
    candidates = [
        os.path.abspath(os.path.join(here, "..", "MEDNet.pypi")),   # vendored as MEDNet.pypi/
        os.path.abspath(os.path.join(here, "..", "MEDNet")),        # vendored as MEDNet/
        os.path.abspath(os.path.join(here, "..", "vendor", "MEDNet.pypi")),
    ]
    for p in candidates:
        if os.path.isdir(p) and p not in sys.path:
            sys.path.insert(0, p)
            break


def build_model(model_type: str,
                input_size: int,
                n_classes: int,
                loss: str,
                class_weights: Optional[Any],
                wave: Optional[str] = None,
                compile_flag: bool = True):
    _ensure_mednet_path()
    from MEDNet.model_factory import ModelFactory
    # Create model (wrapped G3D provides loss/metrics)
    model = ModelFactory.create_model(
        model_type=model_type,
        input_size=input_size,
        n_classes=n_classes,
        loss=loss,
        class_weights=class_weights,
        build=True,
        compile=compile_flag,
        wave=wave,
    )
    return model


def load_weights_best_effort(model, checkpoint_path: str) -> None:
    """Strict weight load: raise if missing or mismatched."""
    if not checkpoint_path or not os.path.exists(checkpoint_path):
        raise FileNotFoundError(f"Checkpoint not found: {checkpoint_path}")
    model.load_weights(checkpoint_path)


def build_models_from_meta(meta) -> Tuple[object, object]:
    """Build skull-strip and segmentation models from meta configuration.

    Returns (ss_model, seg_model). Does not alter any preprocessing/dataflow.
    """
    # Import here to avoid circulars
    from .config import get as cfg

    # Inference sizes
    psize_default = int(cfg(meta, "infer.patch_size", 256))
    psize_ss = int(cfg(meta, "infer.patch_size_ss", psize_default))
    psize_seg = int(cfg(meta, "infer.patch_size_seg", psize_default))

    # SS model
    ss_cfg = cfg(meta, "models.ss") or {}
    if not ss_cfg or not ss_cfg.get("checkpoint"):
        raise ValueError("models.ss.checkpoint is required in meta")
    n_classes_ss = int(ss_cfg.get("n_classes", 2))
    loss_ss = ss_cfg.get("loss", "focal")
    ckpt_ss = ss_cfg["checkpoint"]
    type_ss = ss_cfg.get("type", "uwavevitnet")
    wave_ss = ss_cfg.get("wave", None)
    class_weights_ss = [0.1] * n_classes_ss if "focal" in (loss_ss or "").lower() else None
    ss_model = build_model(type_ss, input_size=psize_ss, n_classes=n_classes_ss, loss=loss_ss, class_weights=class_weights_ss, wave=wave_ss, compile_flag=True)
    load_weights_best_effort(ss_model, ckpt_ss)

    # Seg model
    seg_cfg = cfg(meta, "models.seg") or {}
    if not seg_cfg or not seg_cfg.get("checkpoint"):
        raise ValueError("models.seg.checkpoint is required in meta")
    n_classes_seg = int(seg_cfg.get("n_classes", 4))
    loss_seg = seg_cfg.get("loss", "focal")
    ckpt_seg = seg_cfg["checkpoint"]
    type_seg = seg_cfg.get("type", "uwavevitnet")
    wave_seg = seg_cfg.get("wave", None)
    class_weights_seg = [0.1] * n_classes_seg if "focal" in (loss_seg or "").lower() else None
    seg_model = build_model(type_seg, input_size=psize_seg, n_classes=n_classes_seg, loss=loss_seg, class_weights=class_weights_seg, wave=wave_seg, compile_flag=True)
    load_weights_best_effort(seg_model, ckpt_seg)

    return ss_model, seg_model
