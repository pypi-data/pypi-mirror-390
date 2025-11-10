from __future__ import annotations
import numpy as np
import tensorflow as tf
from typing import Tuple


def _make_weight(ps: int) -> np.ndarray:
    # Smooth window to reduce seams (outer product of 1D Hanns)
    w1 = np.hanning(ps)
    if w1.max() == 0:
        w1 = np.ones(ps)
    w = w1[:, None, None] * w1[None, :, None] * w1[None, None, :]
    w = w.astype(np.float32)
    w /= (w.max() + 1e-8)
    return w


def sliding_window_predict(model,
                           vol4d: np.ndarray,
                           patch_size: int,
                           overlap: int,
                           num_classes: int,
                           batch_size: int = 1) -> np.ndarray:
    """Predict full volume using overlapped sliding windows with blending.

    vol4d: [D,H,W,1]
    Returns softmax predictions [D,H,W,C].
    """
    assert vol4d.ndim == 4 and vol4d.shape[-1] == 1
    D, H, W, _ = vol4d.shape
    ps = patch_size
    st = max(1, ps - overlap)
    # Padding to fit stride grid
    pad_D = (st - (D - ps) % st) % st
    pad_H = (st - (H - ps) % st) % st
    pad_W = (st - (W - ps) % st) % st
    pad_cfg = ((0, pad_D), (0, pad_H), (0, pad_W), (0, 0))
    vol_pad = np.pad(vol4d, pad_cfg, mode="constant")
    Dp, Hp, Wp, _ = vol_pad.shape

    weight = _make_weight(ps)
    acc = np.zeros((Dp, Hp, Wp, num_classes), dtype=np.float32)
    wsum = np.zeros((Dp, Hp, Wp, 1), dtype=np.float32)

    patches = []
    coords = []
    for z in range(0, Dp - ps + 1, st):
        for y in range(0, Hp - ps + 1, st):
            for x in range(0, Wp - ps + 1, st):
                patches.append(vol_pad[z:z+ps, y:y+ps, x:x+ps, :])
                coords.append((z, y, x))
                # batch predict in small groups to control memory
                if len(patches) == batch_size:
                    _accumulate(model, patches, coords, acc, wsum, weight)
                    patches, coords = [], []
    if patches:
        _accumulate(model, patches, coords, acc, wsum, weight)

    # Normalize by weights and crop back
    wsum = np.clip(wsum, 1e-6, None)
    pred_full = acc / wsum
    pred_full = pred_full[:D, :H, :W, :]
    return pred_full


def _accumulate(model, patches, coords, acc, wsum, weight) -> None:
    X = np.stack(patches, axis=0).astype(np.float32)
    X_tf = tf.convert_to_tensor(X)
    preds = model.predict(X_tf, verbose=0)
    # Ensure channel-last [N, ps, ps, ps, C]
    for i, (z, y, x) in enumerate(coords):
        p = preds[i]
        w = weight[..., None]
        acc[z:z+p.shape[0], y:y+p.shape[1], x:x+p.shape[2], :] += p * w
        wsum[z:z+p.shape[0], y:y+p.shape[1], x:x+p.shape[2], :] += w

