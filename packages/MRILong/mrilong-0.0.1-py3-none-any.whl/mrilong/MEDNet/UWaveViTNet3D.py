import os
import tensorflow as tf
from tensorflow.keras import layers as L

from MEDNet.UNet3D import UNet3D
from MEDNet.attentions.WaveletViTND import (
    WaveletTokenizer3D,
    WaveletViTBlock3D,
    WaveletAssembler3D,
)

__all__ = [
    "wavevit_bottleneck_factory",
    "UNetWaveViT3D",
]


def _env_int(name: str, default: int) -> int:
    try:
        v = os.getenv(name)
        return int(v) if v is not None else int(default)
    except Exception:
        return int(default)


def _env_float(name: str, default: float) -> float:
    try:
        v = os.getenv(name)
        return float(v) if v is not None else float(default)
    except Exception:
        return float(default)


def wavevit_bottleneck_factory(
    embed_dim: int = 64,
    levels: int = 1,
    wave: str = "haar",
    *,
    heads: int = 2,
    key_dim: int = 16,
    strength: float = 0.25,
    level_decay: float = 1.0,
    use_orient_mix: bool = True,
    lp_global_if_small: bool = True,
    max_tokens_global: int = 8192,
    qkv_bias: bool = True,
    dwt_compute_dtype: str = "float32",
    prebuild_banks: bool = True,
):
    """Create a deterministic Wavelet-ViT 3D bottleneck callable for UNet3D.

    Returns a function bottleneck(x) -> features using:
      WaveletTokenizer3D -> WaveletViTBlock3D -> WaveletAssembler3D(mode='feature')
    Produces a spatial feature map with `embed_dim` channels.
    """
    E = int(embed_dim)
    Lvl = int(levels)
    H = int(heads)
    KD = int(key_dim)

    # Build layers once, reuse per-call (functional graph friendly)
    tok = WaveletTokenizer3D(levels=Lvl, wave=wave, embed_dim=E,
                             dwt_compute_dtype=dwt_compute_dtype, prebuild_banks=prebuild_banks)
    blk = WaveletViTBlock3D(heads=H, key_dim=KD, strength=float(strength),
                             level_decay=float(level_decay), use_orient_mix=bool(use_orient_mix),
                             lp_global_if_small=bool(lp_global_if_small), max_tokens_global=int(max_tokens_global),
                             qkv_bias=bool(qkv_bias))
    asm = WaveletAssembler3D(levels=Lvl, wave=wave, mode='feature',
                              dwt_compute_dtype=dwt_compute_dtype, prebuild_banks=prebuild_banks)

    def bottleneck(x: tf.Tensor) -> tf.Tensor:
        bands = tok(x)
        bands = blk(bands)
        y = asm(bands)
        # Ensure dtype consistency with upstream
        if y.dtype != x.dtype:
            y = tf.cast(y, x.dtype)
        return y

    return bottleneck


def UNetWaveViT3D(
    input_shape=(32, 32, 32, 1),
    config=(16, 32, 64, 128),
    n_classes=4,
    *,
    embed_dim: int | None = None,
    levels: int = 1,
    wave: str = "haar",
    heads: int = 2,
    key_dim: int = 16,
    strength: float = 0.25,
    level_decay: float = 1.0,
    use_orient_mix: bool = True,
    lp_global_if_small: bool = True,
    max_tokens_global: int = 8192,
    qkv_bias: bool = True,
    dwt_compute_dtype: str = "float32",
    prebuild_banks: bool = True,
    output_kernel_regularizer=None,
    one_hot_encode=True,
    residual=False,
):
    """UNet3D with a deterministic Wavelet-ViT (3D) bottleneck (no VAE).

    The bottleneck operates in the DWT band domain and returns a spatial
    feature with `embed_dim` channels (defaulting to config[-1]).
    """
    E = int(embed_dim) if embed_dim is not None else int(config[-1])
    bottleneck = wavevit_bottleneck_factory(
        embed_dim=E,
        levels=levels,
        wave=wave,
        heads=heads,
        key_dim=key_dim,
        strength=strength,
        level_decay=level_decay,
        use_orient_mix=use_orient_mix,
        lp_global_if_small=lp_global_if_small,
        max_tokens_global=max_tokens_global,
        qkv_bias=qkv_bias,
        dwt_compute_dtype=dwt_compute_dtype,
        prebuild_banks=prebuild_banks,
    )
    return UNet3D(
        input_shape=input_shape,
        config=config,
        n_classes=n_classes,
        bottleneck_fn=bottleneck,
        output_kernel_regularizer=output_kernel_regularizer,
        one_hot_encode=one_hot_encode,
        residual=residual,
    )


if __name__ == "__main__":
    tf.get_logger().setLevel('ERROR')
    tf.random.set_seed(0)
    n = 32
    model = UNetWaveViT3D(
        input_shape=(n, n, n, 1),
        config=(16, 32, 64, 128),
        n_classes=4,
        embed_dim=64,
        levels=1,
        wave='haar',
        heads=2,
        key_dim=16,
        strength=0.5,
        level_decay=1.0,
    )
    x = tf.random.normal((1, n, n, n, 1))
    y = model(x)
    model.summary()
    print("out:", y.shape)
