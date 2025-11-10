""" MRAViT: Multiresolution D-dimensional Attentions for Vision
    Copyright (C) 2025 Kishore Kumar Tarafdar

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.

WaveletViTND.py
Native Wavelet-ViT (1D/2D/3D): DWT tokenizer -> band-wise axial attention (+ optional global on deepest LP)
-> light orientation mixing -> IDWT assembler (tokens or feature).
Keras-graph safe (tensors-only I/O), eager filter-bank prebuild, build-time state creation.
"""
import tensorflow as tf
from tensorflow import keras

# ---------- Robust DWT/IDWT imports ----------
HAVE_1D = False
HAVE_3D = False
try:
    from TFDWT.DWT2DFB import DWT2D, IDWT2D
except Exception:
    from DWT2DFB import DWT2D, IDWT2D

try:
    from TFDWT.DWT3DFB import DWT3D, IDWT3D
    HAVE_3D = True
except Exception:
    try:
        from DWT3DFB import DWT3D, IDWT3D
        HAVE_3D = True
    except Exception:
        HAVE_3D = False

try:
    from TFDWT.DWT1DFB import DWT1D, IDWT1D
    HAVE_1D = True
except Exception:
    try:
        from DWT1DFB import DWT1D, IDWT1D
        HAVE_1D = True
    except Exception:
        HAVE_1D = False


# ---------- Attention blocks ----------
@tf.keras.utils.register_keras_serializable(package="attn")
class GlobalMHSAND(keras.layers.Layer):
    def __init__(self, heads=2, key_dim=16, norm_eps=1e-5, qkv_bias=True, **kw):
        super().__init__(**kw)
        self.heads = int(heads); self.key_dim = int(key_dim)
        self.norm = keras.layers.LayerNormalization(epsilon=norm_eps)
        self.qkv_bias = bool(qkv_bias); self.Conv = None

    def build(self, x_shape):
        dims = len(x_shape) - 2; C = x_shape[-1]
        Conv = {1: keras.layers.Conv1D, 2: keras.layers.Conv2D, 3: keras.layers.Conv3D}[dims]
        self.Conv = Conv
        self.to_q = Conv(self.heads * self.key_dim, 1, use_bias=self.qkv_bias)
        self.to_k = Conv(self.heads * self.key_dim, 1, use_bias=self.qkv_bias)
        self.to_v = Conv(self.heads * self.key_dim, 1, use_bias=self.qkv_bias)
        self.proj = Conv(C, 1, use_bias=self.qkv_bias)

    def call(self, x):
        X = self.norm(x)
        Q = self.to_q(X); K = self.to_k(X); V = self.to_v(X)
        B = tf.shape(x)[0]; spatial = tf.reduce_prod(tf.shape(x)[1:-1])
        h, d = self.heads, self.key_dim

        def pack(t):
            t = tf.reshape(t, [B, spatial, h, d])
            return tf.transpose(t, [0, 2, 1, 3])  # [B,h,T,d]

        Q, K, V = map(pack, (Q, K, V))
        scale = tf.cast(self.key_dim, x.dtype) ** -0.5
        A = tf.nn.softmax(tf.matmul(Q, K, transpose_b=True) * scale, axis=-1)
        Y = tf.matmul(A, V)
        Y = tf.transpose(Y, [0, 2, 1, 3])
        Y = tf.reshape(Y, tf.concat([[B], tf.shape(x)[1:-1], [h * d]], axis=0))
        return self.proj(Y)


@tf.keras.utils.register_keras_serializable(package="attn")
class AxialMHSAND(keras.layers.Layer):
    def __init__(self, heads=2, key_dim=16, norm_eps=1e-5, qkv_bias=True, **kw):
        super().__init__(**kw)
        self.heads = int(heads); self.key_dim = int(key_dim)
        self.norm = keras.layers.LayerNormalization(epsilon=norm_eps)
        self.qkv_bias = bool(qkv_bias); self.Conv = None; self.dims = None

    def build(self, x_shape):
        self.dims = len(x_shape) - 2; C = x_shape[-1]
        self.Conv = {1: keras.layers.Conv1D, 2: keras.layers.Conv2D, 3: keras.layers.Conv3D}[self.dims]
        self.to_q = self.Conv(self.heads * self.key_dim, 1, use_bias=self.qkv_bias)
        self.to_k = self.Conv(self.heads * self.key_dim, 1, use_bias=self.qkv_bias)
        self.to_v = self.Conv(self.heads * self.key_dim, 1, use_bias=self.qkv_bias)
        self.proj = self.Conv(C, 1, use_bias=self.qkv_bias)

    @staticmethod
    def _axis_perm(dims, axis):
        spatial = list(range(1, 1 + dims)); axis_idx = 1 + axis
        others = [i for i in spatial if i != axis_idx]
        perm = [0, axis_idx] + others + [dims + 1]
        inv = [0] * (dims + 2)
        for i, p in enumerate(perm): inv[p] = i
        return perm, inv

    def _attend_along_axis(self, x, axis):
        B = tf.shape(x)[0]; X = self.norm(x)
        Q = self.to_q(X); K = self.to_k(X); V = self.to_v(X)
        h, d = self.heads, self.key_dim
        scale = tf.cast(d, x.dtype) ** -0.5

        perm, inv = self._axis_perm(self.dims, axis)
        Qp = tf.transpose(Q, perm); Kp = tf.transpose(K, perm); Vp = tf.transpose(V, perm)
        shp = tf.shape(Qp); T = shp[1]
        O = tf.reduce_prod(shp[2:-1]) if self.dims > 1 else 1

        def pack(t):
            t = tf.reshape(t, tf.concat([[B, T, O], [h * d]], axis=0))
            t = tf.reshape(t, [B * O, T, h, d])
            return tf.transpose(t, [0, 2, 1, 3])

        Qb = pack(Qp); Kb = pack(Kp); Vb = pack(Vp)
        Ab = tf.nn.softmax(tf.matmul(Qb, Kb, transpose_b=True) * scale, axis=-1)
        Yb = tf.matmul(Ab, Vb)
        Yb = tf.transpose(Yb, [0, 2, 1, 3])
        Yb = tf.reshape(Yb, [B, O, T, h * d])
        Yp = tf.reshape(Yb, tf.concat([[B], [T], shp[2:-1], [h * d]], axis=0)) if self.dims > 1 else tf.reshape(Yb, [B, T, h * d])
        Y = tf.transpose(Yp, inv)
        return self.proj(Y)

    def call(self, x):
        y = x
        for axis in range(self.dims):
            y = self._attend_along_axis(y, axis)
        return y


@tf.keras.utils.register_keras_serializable(package="attn")
class OrientationMix(keras.layers.Layer):
    """Mix across G=2^D-1 HP groups (channel-wise)."""
    def __init__(self, groups, eps=1e-3, **kw):
        super().__init__(**kw)
        self.G = int(groups); self.C = None; self.eps = float(eps); self.W=None

    def build(self, x_shape):
        self.C = x_shape[-1] // self.G
        import numpy as np
        G = self.G
        base = np.eye(G, dtype='float32'); off = np.ones((G, G), dtype='float32') - base
        init_val = base + self.eps * off
        self.W = self.add_weight(name="W", shape=(G, G),
                                 initializer=keras.initializers.Constant(init_val),
                                 trainable=True)

    def call(self, x):
        shp = tf.shape(x); G, C = self.G, self.C
        y = tf.reshape(x, tf.concat([shp[:-1], [G, C]], axis=0))
        y = tf.einsum('gd,...dc->...gc', self.W, y)
        return tf.reshape(y, tf.concat([shp[:-1], [G * C]], axis=0))


# ---------- Tokenizer ----------
@tf.keras.utils.register_keras_serializable(package="attn")
class WaveletTokenizerND(keras.layers.Layer):
    """
    DWT tokenization into levels × subbands with per-band 1×1 projections to embed_dim.
    Returns `bands`: list[level] of {'lp': Tensor[B,*Sℓ,E], 'hp': List[Tensor[B,*Sℓ,E]]}.
    """
    def __init__(self, dims=2, levels=2, wave='sym8', embed_dim=256, norm=True,
                 pad_to_pow2=True, dwt_compute_dtype='float32', prebuild_banks=True, name=None, **kw):
        super().__init__(name=name, **kw)
        assert dims in (1,2,3)
        self.D = int(dims); self.levels = int(levels); self.wave = wave
        self.embed_dim = int(embed_dim); self.norm = bool(norm)
        self.pad_to_pow2 = bool(pad_to_pow2); self.dwt_compute_dtype = dwt_compute_dtype
        self.prebuild_banks = bool(prebuild_banks)

        if self.D==1:
            if not HAVE_1D: raise ImportError("DWT1D/IDWT1D not available")
            self.DWT = DWT1D
        elif self.D==2:
            self.DWT = DWT2D
        else:
            if not HAVE_3D: raise ImportError("DWT3D/IDWT3D not available")
            self.DWT = DWT3D

        self.total_bands = 2**self.D; self.groups = self.total_bands - 1
        # Force DWT layers to compute in float32 to avoid bf16 dtype issues in einsum
        self.dwts = [self.DWT(wave=self.wave, clean=True, dtype='float32') for _ in range(self.levels)]
        self.norm_layer = keras.layers.LayerNormalization(epsilon=1e-5) if self.norm else None
        Conv = {1: keras.layers.Conv1D, 2: keras.layers.Conv2D, 3: keras.layers.Conv3D}[self.D]
        self.proj_lp = Conv(self.embed_dim, 1, use_bias=True)
        self.proj_hp = Conv(self.embed_dim, 1, use_bias=True)

    def _pad_pow2(self, x):
        if not self.pad_to_pow2:
            return x
        shp = tf.shape(x)
        spatial = [shp[1+i] for i in range(self.D)]
        div = tf.constant(2**self.levels, tf.int32)
        adds = [tf.math.floormod(div - tf.math.floormod(n, div), div) for n in spatial]
        paddings = tf.stack([[0,0]] + [[0, a] for a in adds] + [[0,0]], axis=0)
        return tf.pad(x, paddings)

    def _prebuild_banks_eager(self, x_shape):
        with tf.init_scope():
            spatial = [int(s) if (s is not None and s!=-1) else 16 for s in x_shape[1:-1]]
            C = int(x_shape[-1]) if x_shape[-1] is not None else 1
            div = 2**self.levels
            spatial = [s - (s % div) if s % div != 0 else s for s in spatial]
            dummy = tf.zeros([1]+spatial+[C], tf.float32)
            cur = dummy
            for _ in range(self.levels):
                cur = self.dwts[_](cur)[..., :C]

    def build(self, x_shape):
        if self.prebuild_banks: self._prebuild_banks_eager(x_shape)
        super().build(x_shape)

    def call(self, x):
        if self.norm_layer is not None: x = self.norm_layer(x)
        x = self._pad_pow2(x)

        C_in = tf.shape(x)[-1]
        cur = x
        bands = []
        tgt_dtype = tf.as_dtype(self.dwt_compute_dtype)

        for _ in range(self.levels):
            cur32 = tf.cast(cur, tgt_dtype) if cur.dtype != tgt_dtype else cur
            w = self.dwts[_](cur32)             # [B,*Sℓ, total_bands*C_in]
            w = tf.cast(w, x.dtype)
            lp = w[..., :C_in]                  # LL
            hp_concat = w[..., C_in:]           # HPs concatenated
            hp_list = tf.split(hp_concat, num_or_size_splits=self.groups, axis=-1)
            lp_e = self.proj_lp(lp)
            hp_e = [self.proj_hp(h) for h in hp_list]
            bands.append({'lp': lp_e, 'hp': hp_e})
            cur = lp
        return bands


# ---------- Transformer block over bands ----------
@tf.keras.utils.register_keras_serializable(package="attn")
class WaveletViTBlockND(keras.layers.Layer):
    """
    Band-wise axial attention + optional global on deepest LP, OrientationMix, per-level decay, delta residual.
    Input/Output: same bands structure as tokenizer.
    """
    def __init__(self, dims=2, heads=2, key_dim=16, strength=0.25, level_decay=0.6,
                 use_orient_mix=True, lp_global_if_small=True, max_tokens_global=8192, qkv_bias=True,
                 **kw):
        super().__init__(**kw)
        assert dims in (1,2,3)
        self.D = int(dims); self.heads=int(heads); self.key_dim=int(key_dim)
        self.strength = float(strength); self.level_decay = float(level_decay)
        self.use_orient_mix = bool(use_orient_mix)
        self.lp_global_if_small = bool(lp_global_if_small); self.max_tokens_global = int(max_tokens_global)
        self.qkv_bias = bool(qkv_bias)

        self.hp_attn = AxialMHSAND(self.heads, self.key_dim, qkv_bias=self.qkv_bias)
        self.lp_axial = AxialMHSAND(self.heads, self.key_dim, qkv_bias=self.qkv_bias)
        self.lp_global = GlobalMHSAND(self.heads, self.key_dim, qkv_bias=self.qkv_bias)
        self.mixers = None
        self.alpha_hp = None; self.alpha_lp = None
        self.groups = 2**self.D - 1
        self.levels_ = None

    def build(self, bands_shape):
        try:
            self.levels_ = len(bands_shape)
        except Exception:
            self.levels_ = 1
        self.alpha_hp = self.add_weight(name="alpha_hp", shape=(),
                                        initializer=keras.initializers.Constant(0.1), trainable=True)
        self.alpha_lp = self.add_weight(name="alpha_lp", shape=(),
                                        initializer=keras.initializers.Constant(0.1), trainable=True)
        mix_eps = 0.02 * float(self.strength)
        self.mixers = [OrientationMix(self.groups, eps=mix_eps) for _ in range(self.levels_)]
        super().build(bands_shape)

    def _tokens(self, spatial_shape):
        return tf.cast(tf.reduce_prod(spatial_shape), tf.int32)

    def call(self, bands):
        out = []
        L = len(bands)
        for l, d in enumerate(bands):
            lp = d['lp']; hp_list = d['hp']
            level_scale = tf.cast(self.level_decay ** (L-1 - l), lp.dtype)

            hp_proc = [h + (self.alpha_hp * level_scale) * self.hp_attn(h) for h in hp_list]

            if self.use_orient_mix and len(hp_proc) > 1:
                cat = tf.concat(hp_proc, axis=-1)
                cat = self.mixers[l](cat)
                hp_proc = tf.split(cat, num_or_size_splits=len(hp_proc), axis=-1)

            spatial = tf.shape(lp)[1:-1]
            is_last = (l == L - 1)
            def do_axial():  return lp + (self.alpha_lp * level_scale) * self.lp_axial(lp)
            def do_global(): return lp + (self.alpha_lp * level_scale) * self.lp_global(lp)
            if self.lp_global_if_small and is_last:
                T = self._tokens(spatial)
                lp_tokens_small = tf.less_equal(T, tf.cast(self.max_tokens_global, tf.int32))
                lp = tf.cond(lp_tokens_small, do_global, do_axial)
            else:
                lp = do_axial()

            out.append({'lp': lp, 'hp': hp_proc})

        s = tf.cast(self.strength, out[0]['lp'].dtype)
        bands_out = []
        for din, dout in zip(bands, out):
            lp = din['lp'] + s * (dout['lp'] - din['lp'])
            hp = [h_in + s * (h_out - h_in) for h_in, h_out in zip(din['hp'], dout['hp'])]
            bands_out.append({'lp': lp, 'hp': hp})
        return bands_out


# ---------- Assembler ----------
@tf.keras.utils.register_keras_serializable(package="attn")
class WaveletAssemblerND(keras.layers.Layer):
    """
    mode='tokens'  -> pooled deepest LP: [B, E]
    mode='feature' -> IDWT cascade back to feature map: [B, *orig, E]
    Optional cropping can be added via a tensor `pads` if needed (omitted here for simplicity).
    """
    def __init__(self, dims=2, levels=2, wave='sym8', mode='tokens',
                 dwt_compute_dtype='float32', prebuild_banks=True, name=None, **kw):
        super().__init__(name=name, **kw)
        assert dims in (1,2,3); assert mode in ('tokens','feature')
        self.D=int(dims); self.levels=int(levels); self.wave=wave; self.mode=mode
        self.dwt_compute_dtype = dwt_compute_dtype; self.prebuild_banks = bool(prebuild_banks)

        if self.D==1:
            if not HAVE_1D: raise ImportError("IDWT1D not available")
            self.IDWT = IDWT1D
        elif self.D==2:
            self.IDWT = IDWT2D
        else:
            if not HAVE_3D: raise ImportError("IDWT3D not available")
            self.IDWT = IDWT3D

        # Force IDWT layers to compute in float32 to match DWT and avoid bf16 incompatibilities
        self.idwts = [self.IDWT(wave=self.wave, clean=True, dtype='float32') for _ in range(self.levels)]
        self.pool = None

    def build(self, bands_shape):
        if self.mode=='tokens':
            self.pool = keras.layers.GlobalAveragePooling1D() if self.D==1 else \
                        keras.layers.GlobalAveragePooling2D() if self.D==2 else \
                        keras.layers.GlobalAveragePooling3D()
        super().build(bands_shape)

    def _prebuild_banks_eager(self, bands):
        with tf.init_scope():
            spatial = []
            for s in bands[-1]['lp'].shape[1:-1]:
                spatial.append(int(s) if s is not None else 16)
            E = int(bands[-1]['lp'].shape[-1]) if bands[-1]['lp'].shape[-1] is not None else 32
            for l in reversed(range(self.levels)):
                dummy_low = tf.zeros([1]+spatial+[E], tf.float32)
                dummy_hp  = tf.zeros([1]+spatial+[(2**self.D - 1) * E], tf.float32)
                _ = self.idwts[l](tf.concat([dummy_low, dummy_hp], axis=-1))
                spatial = [s*2 for s in spatial]

    def call(self, bands, pads=None):
        if self.mode == 'tokens':
            deepest_lp = bands[-1]['lp']
            return self.pool(deepest_lp)
        if self.prebuild_banks: self._prebuild_banks_eager(bands)

        tgt_dtype = tf.as_dtype(self.dwt_compute_dtype)
        cur = None
        for rev_l, d in enumerate(reversed(bands)):
            low = d['lp']; hp_list = d['hp']
            hp = tf.concat(hp_list, axis=-1) if len(hp_list) > 0 else tf.zeros_like(low)[..., :0]
            merged = tf.concat([low, hp], axis=-1)
            merged32 = tf.cast(merged, tgt_dtype) if merged.dtype != tgt_dtype else merged
            cur = self.idwts[self.levels - 1 - rev_l](merged32)
            cur = tf.cast(cur, bands[0]['lp'].dtype)
        return cur


# ---------- Convenience wrappers ----------
@tf.keras.utils.register_keras_serializable(package="attn")
class WaveletTokenizer1D(WaveletTokenizerND):  
    def __init__(self, **kw): super().__init__(dims=1, **kw)
@tf.keras.utils.register_keras_serializable(package="attn")
class WaveletTokenizer2D(WaveletTokenizerND):  
    def __init__(self, **kw): super().__init__(dims=2, **kw)
@tf.keras.utils.register_keras_serializable(package="attn")
class WaveletTokenizer3D(WaveletTokenizerND):  
    def __init__(self, **kw): super().__init__(dims=3, **kw)

@tf.keras.utils.register_keras_serializable(package="attn")
class WaveletViTBlock1D(WaveletViTBlockND):  
    def __init__(self, **kw): super().__init__(dims=1, **kw)
@tf.keras.utils.register_keras_serializable(package="attn")
class WaveletViTBlock2D(WaveletViTBlockND):  
    def __init__(self, **kw): super().__init__(dims=2, **kw)
@tf.keras.utils.register_keras_serializable(package="attn")
class WaveletViTBlock3D(WaveletViTBlockND):  
    def __init__(self, **kw): super().__init__(dims=3, **kw)

@tf.keras.utils.register_keras_serializable(package="attn")
class WaveletAssembler1D(WaveletAssemblerND):  
    def __init__(self, **kw): super().__init__(dims=1, **kw)
@tf.keras.utils.register_keras_serializable(package="attn")
class WaveletAssembler2D(WaveletAssemblerND):  
    def __init__(self, **kw): super().__init__(dims=2, **kw)
@tf.keras.utils.register_keras_serializable(package="attn")
class WaveletAssembler3D(WaveletAssemblerND):  
    def __init__(self, **kw): super().__init__(dims=3, **kw)


# ---------- Test helpers ----------
def _rel_l2(a, b):
    num = tf.norm(tf.reshape(a - b, [tf.shape(a)[0], -1]), ord='euclidean', axis=1)
    den = tf.norm(tf.reshape(b,     [tf.shape(b)[0], -1]), ord='euclidean', axis=1) + 1e-12
    return tf.reduce_max(num / den)

def _bands_rel_l2(b1, b2):
    vals = []
    for d1, d2 in zip(b1, b2):
        vals.append(_rel_l2(d1['lp'], d2['lp']))
        for h1, h2 in zip(d1['hp'], d2['hp']):
            vals.append(_rel_l2(h1, h2))
    return float(tf.reduce_max(tf.stack(vals)))

def _bandspace_max_abs_delta(b_in, b_out):
    out = []
    for l, (d0, d1) in enumerate(zip(b_in, b_out)):
        lp = float(tf.reduce_max(tf.abs(d1['lp'] - d0['lp'])))
        c0 = tf.concat(d0['hp'], axis=-1) if d0['hp'] else tf.zeros_like(d0['lp'])[..., :0]
        c1 = tf.concat(d1['hp'], axis=-1) if d1['hp'] else tf.zeros_like(d1['lp'])[..., :0]
        hp = float(tf.reduce_max(tf.abs(c1 - c0)))
        out.append((lp, hp))
    return out

def _grad_report(model, x, y, keys=None):
    keys = keys or []
    with tf.GradientTape() as tape:
        yhat = model(x, training=True)
        loss = tf.reduce_mean(tf.square(yhat - y))
    grads = tape.gradient(loss, model.trainable_variables)
    total = sum(float(tf.norm(g)) for g in grads if g is not None)
    bucket = {k:0.0 for k in keys}
    for var, g in zip(model.trainable_variables, grads):
        if g is None: continue
        name = var.name
        for k in keys:
            if k in name:
                bucket[k] += float(tf.norm(g))
    print("Grad totals:", {k: round(v, 6) for k,v in bucket.items()}, "| total:", round(total, 6))
    return total, bucket


# ---------- Self-tests & demos ----------
# ------------------------- Self-tests & demos -------------------------
if __name__ == "__main__":
    try:
        has_gpu = len(tf.config.list_physical_devices('GPU')) > 0
        if has_gpu:
            tf.keras.mixed_precision.set_global_policy('mixed_float16')
            print("Mixed precision: enabled (GPU detected)")
        else:
            print("Mixed precision: skipped (no GPU)")
    except Exception:
        print("Mixed precision: skipped")

    tf.random.set_seed(0)
    print("Running WaveletViTND self-tests (PR + grad + serialization) ...")

    # ========================= 2D (tokens) LP-only (HP frozen to silence warnings) =========================
    print("\n=== 2D (tokens, LP-only) ===")
    B, N, C = 2, 128, 3
    x2 = tf.random.normal((B, N, N, C))

    # --- PR-2: DWT->IDWT transform round-trip sanity check (2D) ---
    try:
        dwt_rt = DWT2D(wave='sym8', clean=True)
        idwt_rt = IDWT2D(wave='sym8', clean=True)
        x2_rt_in = tf.cast(x2, tf.float32)  # compute in fp32 for crisp PR
        w_rt = dwt_rt(x2_rt_in)
        x2_rt = idwt_rt(w_rt)
        rel_rt = float(_rel_l2(x2_rt, x2_rt_in))
        print("2D | PR-2 (transform round-trip) rel-L2:", rel_rt)
    except Exception as e:
        print("2D | PR-2 check skipped:", e)

    tok2_lp = WaveletTokenizer2D(levels=2, wave='sym8', embed_dim=64)
    b2_in = tok2_lp(x2)
    blk2_lp_pr = WaveletViTBlock2D(heads=2, key_dim=16, strength=0.0)
    b2_out_pr = blk2_lp_pr(b2_in)
    print("2D | PR (strength=0) bands rel-L2:", _bands_rel_l2(b2_out_pr, b2_in))

    blk2_lp = WaveletViTBlock2D(heads=2, key_dim=16, strength=0.25)
    b2_out = blk2_lp(b2_in)
    print("2D | default strength bands rel-L2:", _bands_rel_l2(b2_out, b2_in))

    asm2_lp = WaveletAssembler2D(levels=2, wave='sym8', mode='tokens')
    z2 = asm2_lp(bands=b2_out)
    print("2D | pooled tokens shape:", z2.shape)

    # Build LP-only classifier and freeze HP path to avoid grad warnings
    inp2_lp = keras.Input((N, N, C))
    tb_lp = tok2_lp(inp2_lp)
    tb_lp = blk2_lp(tb_lp)
    vec_lp = asm2_lp(bands=tb_lp)
    logits2_lp = keras.layers.Dense(10)(vec_lp)
    model2_lp = keras.Model(inp2_lp, logits2_lp, name="wavelet_vit_2d_tokens_lp")

    tok2_lp.proj_hp.trainable = False
    try: blk2_lp.alpha_hp.assign(0.0)
    except Exception: pass
    blk2_lp.alpha_hp.trainable = False
    blk2_lp.hp_attn.trainable = False
    for m in blk2_lp.mixers: m.trainable = False

    model2_lp.compile(optimizer="adam", loss="mse", jit_compile=False)
    model2_lp.summary()
    model2_lp.fit(tf.random.normal((2, N, N, C)),
                  tf.random.normal((2, 10)), epochs=1, verbose=1)

    # Serialization round-trip (clone) — Keras 3 style
    try:
        model2_lp_clone = keras.models.clone_model(model2_lp)
    except TypeError:
        cfg = keras.saving.serialize_keras_object(model2_lp)
        model2_lp_clone = keras.saving.deserialize_keras_object(cfg)
    model2_lp_clone.set_weights(model2_lp.get_weights())
    model2_lp_clone.compile(optimizer="adam", loss="mse", jit_compile=False)
    model2_lp_clone.fit(tf.random.normal((2, N, N, C)),
                        tf.random.normal((2, 10)), epochs=1, verbose=1)

    # ========================= 2D (tokens) LP+HP tokens (HP gets gradients) =========================
    print("\n=== 2D (tokens, LP+HP pooled) ===")
    tok2_all = WaveletTokenizer2D(levels=2, wave='sym8', embed_dim=64)
    blk2_all = WaveletViTBlock2D(heads=2, key_dim=16, strength=0.25)
    asm2_all = WaveletAssembler2D(levels=2, wave='sym8', mode='tokens')

    inp2_all = keras.Input((N, N, C))
    tb_all = tok2_all(inp2_all)
    tb_all = blk2_all(tb_all)
    lp_vec = asm2_all(bands=tb_all)
    gap2 = keras.layers.GlobalAveragePooling2D()
    hp_vecs = [gap2(h) for lvl in tb_all for h in lvl['hp']]
    feat_all = keras.layers.Concatenate()([lp_vec] + hp_vecs) if hp_vecs else lp_vec
    logits2_all = keras.layers.Dense(10)(feat_all)
    model2_all = keras.Model(inp2_all, logits2_all, name="wavelet_vit_2d_tokens_lphp")
    model2_all.compile(optimizer="adam", loss="mse", jit_compile=False)
    _ = _grad_report(model2_all,
                     tf.random.normal((2, N, N, C)),
                     tf.random.normal((2, 10)),
                     keys=["proj_hp", "alpha_hp", "hp_attn", "orientation_mix"])
    model2_all.fit(tf.random.normal((2, N, N, C)),
                   tf.random.normal((2, 10)), epochs=1, verbose=1)

    # ========================= 3D (feature) =========================
    if HAVE_3D:
        print("\n=== 3D (feature) ===")
        try:
            orig_policy = tf.keras.mixed_precision.global_policy().name
            tf.keras.mixed_precision.set_global_policy('float32')
            print("3D test: precision policy -> float32")
        except Exception:
            orig_policy = None

        B3, D3, C3 = 1, 32, 1
        x3 = tf.random.normal((B3, D3, D3, D3, C3))

        # --- PR-2: DWT->IDWT transform round-trip sanity check (3D) ---
        try:
            dwt3_rt = DWT3D(wave='haar', clean=True)
            idwt3_rt = IDWT3D(wave='haar', clean=True)
            x3_rt_in = tf.cast(x3, tf.float32)
            w3_rt = dwt3_rt(x3_rt_in)
            x3_rt = idwt3_rt(w3_rt)
            rel3_rt = float(_rel_l2(x3_rt, x3_rt_in))
            print("3D | PR-2 (transform round-trip) rel-L2:", rel3_rt)
        except Exception as e:
            print("3D | PR-2 check skipped:", e)

        tok3 = WaveletTokenizer3D(levels=2, wave='haar', embed_dim=32)
        b3_in = tok3(x3)
        blk3_pr = WaveletViTBlock3D(heads=2, key_dim=8, strength=0.0)
        b3_out_pr = blk3_pr(b3_in)
        print("3D | PR (strength=0) bands rel-L2:", _bands_rel_l2(b3_out_pr, b3_in))

        blk3 = WaveletViTBlock3D(heads=2, key_dim=12, strength=1.0, level_decay=1.0)
        b3_out = blk3(b3_in)
        band_deltas = _bandspace_max_abs_delta(b3_in, b3_out)
        print("3D | band-space max|Δ| per level (LP, HP):", band_deltas)

        asm3 = WaveletAssembler3D(levels=2, wave='haar', mode='feature')
        y3_in = asm3(bands=b3_in)
        y3    = asm3(bands=b3_out)
        print("3D | feature rel-L2 (strength=1):", float(_rel_l2(y3, y3_in)))

        inp3 = keras.Input((D3, D3, D3, C3))
        tb3 = tok3(inp3); tb3 = blk3(tb3)
        feat3 = asm3(bands=tb3)
        out3 = keras.layers.Conv3D(4, 1)(feat3)
        model3 = keras.Model(inp3, out3, name="wavelet_vit_3d_feature")
        model3.compile(optimizer="adam", loss="mse", jit_compile=False)
        _ = _grad_report(model3,
                         tf.random.normal((1, D3, D3, D3, C3)),
                         tf.random.normal((1, D3, D3, D3, 4)),
                         keys=["proj_hp", "alpha_hp", "hp_attn", "orientation_mix"])
        model3.summary()
        model3.fit(tf.random.normal((1, D3, D3, D3, C3)),
                   tf.random.normal((1, D3, D3, D3, 4)), epochs=1, verbose=1)

        if orig_policy:
            tf.keras.mixed_precision.set_global_policy(orig_policy)
            print(f"Precision policy restored -> {orig_policy}")

    # ========================= 1D (tokens) =========================
    if HAVE_1D:
        print("\n=== 1D (tokens) ===")
        B1, T1, C1 = 2, 256, 3
        x1 = tf.random.normal((B1, T1, C1))

        # --- PR-2: DWT->IDWT transform round-trip sanity check (1D) ---
        try:
            dwt1_rt = DWT1D(wave='db8', clean=True)
            idwt1_rt = IDWT1D(wave='db8', clean=True)
            x1_rt_in = tf.cast(x1, tf.float32)
            w1_rt = dwt1_rt(x1_rt_in)
            x1_rt = idwt1_rt(w1_rt)
            rel1_rt = float(_rel_l2(x1_rt, x1_rt_in))
            print("1D | PR-2 (transform round-trip) rel-L2:", rel1_rt)
        except Exception as e:
            print("1D | PR-2 check skipped:", e)

        tok1 = WaveletTokenizer1D(levels=3, wave='db8', embed_dim=32)
        b1_in = tok1(x1)
        blk1_pr = WaveletViTBlock1D(heads=2, key_dim=8, strength=0.0)
        b1_out_pr = blk1_pr(b1_in)
        print("1D | PR (strength=0) bands rel-L2:", _bands_rel_l2(b1_out_pr, b1_in))

        blk1 = WaveletViTBlock1D(heads=2, key_dim=8, strength=0.25)
        b1_out = blk1(b1_in)
        print("1D | default strength bands rel-L2:", _bands_rel_l2(b1_out, b1_in))

        asm1 = WaveletAssembler1D(levels=3, wave='db8', mode='tokens')
        z1 = asm1(bands=b1_out)
        print("1D | pooled tokens shape:", z1.shape)

        inp1 = keras.Input((T1, C1))
        tb1 = tok1(inp1); tb1 = blk1(tb1)
        tvec1 = asm1(bands=tb1)
        out1 = keras.layers.Dense(5)(tvec1)
        model1 = keras.Model(inp1, out1, name="wavelet_vit_1d_tokens")
        model1.compile(optimizer="adam", loss="mse", jit_compile=False)
        model1.summary()
        model1.fit(tf.random.normal((2, T1, C1)),
                   tf.random.normal((2, 5)), epochs=1, verbose=1)

    print("\nDone.")
