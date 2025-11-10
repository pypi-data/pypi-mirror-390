# DWTSelfAttentionND.py
# Unified 1D/2D/3D: DWT → per-subband AXIAL self-attention (global-on-deep-LP if small) → IDWT.
# Simple API: one user knob `strength` (default 0.25). No manual gamma juggling.
# Includes eager prebuild of DWT/IDWT banks to avoid FuncGraph “out-of-scope tensor” issues.
# Author: kkt+x

import tensorflow as tf
from tensorflow import keras

# ------------------------- Robust imports for your fast DWT/IDWT -------------------------
HAVE_1D = False
HAVE_3D = False

# 1D (optional)
try:
    from TFDWT.DWT1DFB import DWT1D, IDWT1D
    HAVE_1D = True
except Exception:
    try:
        from DWT1DFB import DWT1D, IDWT1D
        HAVE_1D = True
    except Exception:
        HAVE_1D = False  # OK; 1D tests will be skipped

# 2D (required)
try:
    from TFDWT.DWT2DFB import DWT2D, IDWT2D
except Exception:
    from DWT2DFB import DWT2D, IDWT2D  # provided by you

# 3D (optional)
try:
    from TFDWT.DWT3DFB import DWT3D, IDWT3D
    HAVE_3D = True
except Exception:
    try:
        from DWT3DFB import DWT3D, IDWT3D
        HAVE_3D = True
    except Exception:
        HAVE_3D = False

# ------------------------- Building blocks -------------------------
@tf.keras.utils.register_keras_serializable(package="attn")
class GlobalMHSAND(keras.layers.Layer):
    """Global MHSA on ND tensors shaped [B, *spatial, C]. Used only for deep LP if small."""
    def __init__(self, heads=2, key_dim=16, norm_eps=1e-5, qkv_bias=True, **kw):
        super().__init__(**kw)
        self.heads = int(heads)
        self.key_dim = int(key_dim)
        self.norm = keras.layers.LayerNormalization(epsilon=norm_eps)
        self.qkv_bias = bool(qkv_bias)
        self.Conv = None  # chosen in build based on dims

    def build(self, x_shape):
        C = x_shape[-1]
        dims = len(x_shape) - 2
        Conv = {1: keras.layers.Conv1D, 2: keras.layers.Conv2D, 3: keras.layers.Conv3D}[dims]
        self.Conv = Conv
        self.to_q = Conv(self.heads * self.key_dim, 1, use_bias=self.qkv_bias)
        self.to_k = Conv(self.heads * self.key_dim, 1, use_bias=self.qkv_bias)
        self.to_v = Conv(self.heads * self.key_dim, 1, use_bias=self.qkv_bias)
        self.proj = Conv(C, 1, use_bias=self.qkv_bias)

    def call(self, x):
        X = self.norm(x)
        Q = self.to_q(X); K = self.to_k(X); V = self.to_v(X)
        B = tf.shape(x)[0]
        spatial = tf.reduce_prod(tf.shape(x)[1:-1])
        h, d = self.heads, self.key_dim

        def pack(t):
            t = tf.reshape(t, [B, spatial, h, d])    # [B,T,h,d]
            return tf.transpose(t, [0, 2, 1, 3])     # [B,h,T,d]
        Q, K, V = map(pack, (Q, K, V))

        scale = tf.cast(self.key_dim, x.dtype) ** -0.5
        A = tf.nn.softmax(tf.matmul(Q, K, transpose_b=True) * scale, axis=-1)  # [B,h,T,T]
        Y = tf.matmul(A, V)                                                    # [B,h,T,d]
        Y = tf.transpose(Y, [0, 2, 1, 3])                                      # [B,T,h,d]
        Y = tf.reshape(Y, tf.concat([[B], tf.shape(x)[1:-1], [h * d]], axis=0))
        return self.proj(Y)

@tf.keras.utils.register_keras_serializable(package="attn")
class AxialMHSAND(keras.layers.Layer):
    """
    Factorized axial MHSA for ND (1D/2D/3D). Sweeps each spatial axis sequentially.
    Complexity is far below global in 3D; bias=True so it's non-degenerate at init.
    """
    def __init__(self, heads=2, key_dim=16, norm_eps=1e-5, qkv_bias=True, **kw):
        super().__init__(**kw)
        self.heads = int(heads)
        self.key_dim = int(key_dim)
        self.norm = keras.layers.LayerNormalization(epsilon=norm_eps)
        self.qkv_bias = bool(qkv_bias)
        self.Conv = None
        self.dims = None

    def build(self, x_shape):
        self.dims = len(x_shape) - 2
        C = x_shape[-1]
        self.Conv = {1: keras.layers.Conv1D, 2: keras.layers.Conv2D, 3: keras.layers.Conv3D}[self.dims]
        self.to_q = self.Conv(self.heads * self.key_dim, 1, use_bias=self.qkv_bias)
        self.to_k = self.Conv(self.heads * self.key_dim, 1, use_bias=self.qkv_bias)
        self.to_v = self.Conv(self.heads * self.key_dim, 1, use_bias=self.qkv_bias)
        self.proj = self.Conv(C, 1, use_bias=self.qkv_bias)

    @staticmethod
    def _axis_perm(dims, axis):
        spatial = list(range(1, 1 + dims))
        axis_idx = 1 + axis
        others = [i for i in spatial if i != axis_idx]
        perm = [0, axis_idx] + others + [dims + 1]
        inv = [0] * (dims + 2)
        for i, p in enumerate(perm): inv[p] = i
        return perm, inv

    def _attend_along_axis(self, x, axis):
        B = tf.shape(x)[0]
        X = self.norm(x)
        Q = self.to_q(X); K = self.to_k(X); V = self.to_v(X)
        h, d = self.heads, self.key_dim
        scale = tf.cast(d, x.dtype) ** -0.5

        perm, inv = self._axis_perm(self.dims, axis)
        Qp = tf.transpose(Q, perm); Kp = tf.transpose(K, perm); Vp = tf.transpose(V, perm)
        shp = tf.shape(Qp); T = shp[1]
        O = tf.reduce_prod(shp[2:-1]) if self.dims > 1 else 1

        def pack(t):
            # [B, T, *O, h*d] -> [B*O, h, T, d]
            t = tf.reshape(t, tf.concat([[B, T, O], [h * d]], axis=0))
            t = tf.reshape(t, [B * O, T, h, d])
            return tf.transpose(t, [0, 2, 1, 3])

        Qb = pack(Qp); Kb = pack(Kp); Vb = pack(Vp)
        logits = tf.matmul(Qb, Kb, transpose_b=True) * scale   # [B*O,h,T,T]
        Ab = tf.nn.softmax(logits, axis=-1)
        Yb = tf.matmul(Ab, Vb)                                  # [B*O,h,T,d]
        Yb = tf.transpose(Yb, [0, 2, 1, 3])                     # [B*O,T,h,d]
        Yb = tf.reshape(Yb, [B, O, T, h * d])
        Yp = tf.reshape(Yb, tf.concat([[B], [T], shp[2:-1], [h * d]], axis=0)) if self.dims > 1 \
             else tf.reshape(Yb, [B, T, h * d])
        Y = tf.transpose(Yp, inv)
        return self.proj(Y)

    def call(self, x):
        y = x
        for axis in range(self.dims):       # 1D: one pass; 2D: H,W; 3D: D,H,W
            y = self._attend_along_axis(y, axis)
        return y

@tf.keras.utils.register_keras_serializable(package="attn")
class OrientationMix(keras.layers.Layer):
    """Mix across G=2^D-1 HP groups with a shared GxG matrix (channel-wise)."""
    def __init__(self, groups, eps=1e-3, **kw):
        super().__init__(**kw)
        self.G = int(groups)
        self.C = None
        self.eps = float(eps)
        self.W = None

    def build(self, x_shape):
        self.C = x_shape[-1] // self.G
        import numpy as np
        G = self.G
        base = np.eye(G, dtype='float32')
        off  = np.ones((G, G), dtype='float32') - base
        init_val = base + self.eps * off  # I + eps*(1-I)
        self.W = self.add_weight(
            name="W",
            shape=(G, G),
            initializer=keras.initializers.Constant(init_val),
            trainable=True,
        )

    def call(self, x):
        shp = tf.shape(x)
        G, C = self.G, self.C
        y = tf.reshape(x, tf.concat([shp[:-1], [G, C]], axis=0))     # [..., G, C]
        y = tf.einsum('gd,...dc->...gc', self.W, y)                  # [..., G, C]
        return tf.reshape(y, tf.concat([shp[:-1], [G * C]], axis=0))

# ------------------------- Main ND block -------------------------
@tf.keras.utils.register_keras_serializable(package="attn")
class DWTSelfAttentionND(keras.layers.Layer):
    """
    ND DWT → per-subband AXIAL self-attention → IDWT.
    Simple API:
      - strength: float in [0,1], default 0.25 (visible but mild change).
      - lp_global_if_small: bool; allow global attention on deepest LP if tokens ≤ cap.
      - max_tokens_global: token cap for ^ (default 8192).
      - heads/key_dim: attention size (small defaults).
      - level_decay: per-level decay (coarser stronger; default 0.6).
      - dwt_compute_dtype: dtype used inside DWT/IDWT ('float32' default).
      - prebuild_banks: eagerly build DWT/IDWT once to avoid FuncGraph scope issues.
    Everything else is automatic & economical.
    """
    def __init__(self, dims=2, levels=2, wave='db2',
                 strength=0.25,
                 lp_global_if_small=True, max_tokens_global=8192,
                 heads=2, key_dim=16, qkv_bias=True,
                 use_orient_mix=True, level_decay=0.6,
                 dwt_compute_dtype='float32',
                 prebuild_banks=True,
                 name=None, **kw):
        super().__init__(name=name, **kw)
        assert dims in (1, 2, 3), "dims must be 1, 2, or 3"
        self.D = int(dims)
        self.levels = int(levels)
        self.wave = wave
        self.strength = float(strength)
        self.lp_global_if_small = bool(lp_global_if_small)
        self.max_tokens_global = int(max_tokens_global)
        self.heads = int(heads)
        self.key_dim = int(key_dim)
        self.qkv_bias = bool(qkv_bias)
        self.use_orient_mix = bool(use_orient_mix)
        self.level_decay = float(level_decay)
        self.dwt_compute_dtype = dwt_compute_dtype
        self.prebuild_banks = bool(prebuild_banks)

        # Choose bank classes
        if self.D == 1:
            if not HAVE_1D: raise ImportError("DWT1D/IDWT1D not available")
            self.DWT, self.IDWT = DWT1D, IDWT1D
        elif self.D == 2:
            self.DWT, self.IDWT = DWT2D, IDWT2D
        else:
            if not HAVE_3D: raise ImportError("DWT3D/IDWT3D not available")
            self.DWT, self.IDWT = DWT3D, IDWT3D

        self.total_bands = 2 ** self.D     # includes LL
        self.groups = self.total_bands - 1 # number of HP groups per level

        # Analysis/Synthesis stacks
        self.dwts  = [self.DWT(wave=self.wave, clean=True)  for _ in range(self.levels)]
        self.idwts = [self.IDWT(wave=self.wave, clean=True) for _ in range(self.levels)]

        # Shared attention modules (simple & light)
        self.hp_attn = None   # axial, shared across bands & levels
        self.lp_axial = None  # axial for LP (all levels)
        self.lp_global = None # global for deepest LP if small
        self.mixers = []      # per level orientation mixers

        # tiny internal scales to ensure non-identity even at init
        self.alpha_hp = None
        self.alpha_lp = None

    # ----- Helpers -----
    def _tokens(self, spatial_shape):
        t = tf.reduce_prod(spatial_shape)
        return tf.cast(t, tf.int32)

    def _use_deep_global(self, spatial_shape, is_last: bool):
        if not self.lp_global_if_small or not is_last:
            return tf.constant(False)
        T = self._tokens(spatial_shape)
        cap = tf.cast(self.max_tokens_global, tf.int32)
        return tf.less_equal(T, cap)

    def _split_concat(self, concat_hp):
        Cg = tf.shape(concat_hp)[-1] // self.groups
        return tf.split(concat_hp, num_or_size_splits=self.groups, axis=-1), Cg

    def _join_concat(self, hp_list): return tf.concat(hp_list, axis=-1)

    # ----- DWT/IDWT with safe dtype casting -----
    def _dwt_level(self, l, x):
        tgt = tf.as_dtype(self.dwt_compute_dtype)
        x32 = tf.cast(x, tgt) if x.dtype != tgt else x
        w32 = self.dwts[l](x32)
        return tf.cast(w32, self.compute_dtype or tf.float32)

    def _idwt_level(self, l, w):
        tgt = tf.as_dtype(self.dwt_compute_dtype)
        w32 = tf.cast(w, tgt) if w.dtype != tgt else w
        y32 = self.idwts[l](w32)
        return tf.cast(y32, self.compute_dtype or tf.float32)

    # ----- Eager prebuild to avoid FuncGraph scope issues -----
    def _prebuild_banks_eager(self, x_shape):
        """Force-build each DWT/IDWT in eager so cached matrices/ops are graph-safe."""
        with tf.init_scope():  # leave any FuncGraph; run eagerly
            # static sizes; fall back to small defaults if None
            spatial = [int(s) if (s is not None and s != -1) else 16 for s in x_shape[1:-1]]
            C = int(x_shape[-1]) if x_shape[-1] is not None else 1

            # ensure even divisibility by 2**levels
            div = 2 ** self.levels
            spatial = [s - (s % div) if s % div != 0 else s for s in spatial]
            dummy = tf.zeros([1] + spatial + [C], dtype=tf.float32)

            cur = dummy
            w_per_level = []
            for l in range(self.levels):
                w = self.dwts[l](cur)   # builds DWT(l) eagerly
                w_per_level.append(w)
                cur = w[..., :C]        # next level's LP
            for l in reversed(range(self.levels)):
                _ = self.idwts[l](w_per_level[l])  # builds IDWT(l) eagerly

    # ----- Build -----
    def build(self, x_shape):
        # shared attention modules
        self.hp_attn  = AxialMHSAND(self.heads, self.key_dim, qkv_bias=self.qkv_bias)
        self.lp_axial = AxialMHSAND(self.heads, self.key_dim, qkv_bias=self.qkv_bias)
        self.lp_global = GlobalMHSAND(self.heads, self.key_dim, qkv_bias=self.qkv_bias)

        # Orientation mixer eps tied to user strength (auto-visible but mild)
        if self.use_orient_mix:
            mix_eps = 0.02 * float(self.strength)  # ~2% cross-orientation at strength=1
            self.mixers = [OrientationMix(self.groups, eps=mix_eps) for _ in range(self.levels)]

        # tiny internal scales so attention path is active right away
        self.alpha_hp = self.add_weight(
            name='alpha_hp', shape=(),
            initializer=tf.keras.initializers.Constant(0.1), trainable=True)
        self.alpha_lp = self.add_weight(
            name='alpha_lp', shape=(),
            initializer=tf.keras.initializers.Constant(0.1), trainable=True)

        # prebuild DWT/IDWT banks eagerly to avoid out-of-scope tensors
        if self.prebuild_banks:
            self._prebuild_banks_eager(x_shape)

        # cache dtype
        self._model_dtype = self.compute_dtype or tf.float32
        super().build(x_shape)

    # ----- Main -----
    def call(self, x, training=False):
        C = tf.shape(x)[-1]
        highs = []
        cur = x

        # Analysis cascade
        for l in range(self.levels):
            w = self._dwt_level(l, cur)            # [B,*S/2, total_bands*C]
            low = w[..., :C]                       # LL
            hp  = w[..., C:]                       # concatenated HP bands
            highs.append((low, hp))
            cur = low

        low = cur

        # Synthesis with per-level processing (fine→coarse)
        for rev_l, (low_l, hp) in enumerate(reversed(highs)):
            l = self.levels - 1 - rev_l

            # Per-level decay (coarser edits stronger)
            level_scale = tf.cast(self.level_decay ** (self.levels - 1 - l), x.dtype)

            # HP: split bands, apply shared axial attention + residual with small scale
            bands, _ = self._split_concat(hp)
            bands_out = [b + (self.alpha_hp * level_scale) * self.hp_attn(b) for b in bands]
            hp = self._join_concat(bands_out)
            if self.use_orient_mix:
                hp = self.mixers[l](hp)

            # LP: axial at all levels; optional global at deepest if small
            spatial = tf.shape(low)[1:-1]
            use_global = self._use_deep_global(spatial, is_last=(l == self.levels - 1))

            def lp_global():
                return low + (self.alpha_lp * level_scale) * self.lp_global(low)

            def lp_axial():
                return low + (self.alpha_lp * level_scale) * self.lp_axial(low)

            low = tf.cond(use_global, lp_global, lp_axial)

            merged = tf.concat([low, hp], axis=-1)
            low = self._idwt_level(l, merged)

        # Delta residual: single, intuitive knob
        strength = tf.cast(self.strength, x.dtype)
        return x + strength * (low - x)

    # ----- Config for serialization -----
    def get_config(self):
        return {
            "dims": self.D, "levels": self.levels, "wave": self.wave,
            "strength": self.strength,
            "lp_global_if_small": self.lp_global_if_small,
            "max_tokens_global": self.max_tokens_global,
            "heads": self.heads, "key_dim": self.key_dim, "qkv_bias": self.qkv_bias,
            "use_orient_mix": self.use_orient_mix, "level_decay": self.level_decay,
            "dwt_compute_dtype": self.dwt_compute_dtype,
            "prebuild_banks": self.prebuild_banks,
            "name": self.name,
        }

# ------------------------- Thin wrappers -------------------------
@tf.keras.utils.register_keras_serializable(package="attn")
class DWTSelfAttention1D(DWTSelfAttentionND):
    def __init__(self, **kw): super().__init__(dims=1, **kw)

@tf.keras.utils.register_keras_serializable(package="attn")
class DWTSelfAttention2D(DWTSelfAttentionND):
    def __init__(self, **kw): super().__init__(dims=2, **kw)

@tf.keras.utils.register_keras_serializable(package="attn")
class DWTSelfAttention3D(DWTSelfAttentionND):
    def __init__(self, **kw): super().__init__(dims=3, **kw)

# ------------------------- Self-tests & quick demos -------------------------
def _rel_l2(a, b):
    num = tf.norm(tf.reshape(a - b, [tf.shape(a)[0], -1]), ord='euclidean', axis=1)
    den = tf.norm(tf.reshape(b,     [tf.shape(b)[0], -1]), ord='euclidean', axis=1) + 1e-12
    return tf.reduce_max(num / den)

if __name__ == '__main__':
    # Mixed precision only if GPU (DWT/IDWT run in fp32 internally anyway)
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
    print("Running DWTNDAttention self-tests with PR checks...")

    # ========================= 2D =========================
    print("\n=== 2D ===")
    B, N, C = 1, 128, 3
    x2 = tf.random.normal((B, N, N, C))

    # PR-1: Residual gate PR (strength=0 ⇒ y ≈ x)
    layer2_pr1 = DWTSelfAttention2D(levels=2, wave='haar', strength=0.0)
    y2_pr1 = layer2_pr1(x2)
    print("2D | PR-1 (residual, strength=0) rel-L2:", float(_rel_l2(y2_pr1, x2)))

    # PR-2: Transform PR (neutralize attention; DWT→IDWT ≈ identity)
    layer2_pr2 = DWTSelfAttention2D(levels=2, wave='haar', strength=1.0,
                                    use_orient_mix=False, dwt_compute_dtype='float32')
    _ = layer2_pr2(x2)                  # build vars
    layer2_pr2.alpha_hp.assign(0.0)     # neutralize HP edits
    layer2_pr2.alpha_lp.assign(0.0)     # neutralize LP edits
    y2_pr2 = layer2_pr2(x2)
    print("2D | PR-2 (transform round-trip) rel-L2:", float(_rel_l2(y2_pr2, x2)))

    # Default demo (non-identity by default, strength=0.25)
    layer2 = DWTSelfAttention2D(levels=2, wave='haar')
    y2 = layer2(x2)
    print("2D | default strength rel-L2:", float(_rel_l2(y2, x2)))

    model2 = keras.Sequential([keras.Input((N, N, C)), layer2, keras.layers.Conv2D(C, 1)])
    model2.compile(optimizer='adam', loss='mse', jit_compile=False)
    model2.summary()
    model2.fit(tf.random.normal((2, N, N, C)),
               tf.random.normal((2, N, N, C)),
               epochs=1, verbose=1)

    # ========================= 1D (optional) =========================
    if HAVE_1D:
        print("\n=== 1D ===")
        T = 256
        x1 = tf.random.normal((B, T, C))

        layer1_pr1 = DWTSelfAttention1D(levels=3, wave='haar', strength=0.0)
        y1_pr1 = layer1_pr1(x1)
        print("1D | PR-1 (residual, strength=0) rel-L2:", float(_rel_l2(y1_pr1, x1)))

        layer1_pr2 = DWTSelfAttention1D(levels=3, wave='haar', strength=1.0,
                                        use_orient_mix=False, dwt_compute_dtype='float32')
        _ = layer1_pr2(x1)
        layer1_pr2.alpha_hp.assign(0.0); layer1_pr2.alpha_lp.assign(0.0)
        y1_pr2 = layer1_pr2(x1)
        print("1D | PR-2 (transform round-trip) rel-L2:", float(_rel_l2(y1_pr2, x1)))

        layer1 = DWTSelfAttention1D(levels=3, wave='haar')
        y1 = layer1(x1)
        print("1D | default strength rel-L2:", float(_rel_l2(y1, x1)))

        model1 = keras.Sequential([keras.Input((T, C)), layer1, keras.layers.Conv1D(C, 1)])
        model1.compile(optimizer='adam', loss='mse', jit_compile=False)
        model1.summary()
        model1.fit(tf.random.normal((2, T, C)),
                   tf.random.normal((2, T, C)),
                   epochs=1, verbose=1)

    # ========================= 3D (optional) =========================
    if HAVE_3D:
        print("\n=== 3D ===")
        D3 = 64
        x3 = tf.random.normal((B, D3, D3, D3, C))

        layer3_pr1 = DWTSelfAttention3D(levels=2, wave='haar', strength=0.0)
        y3_pr1 = layer3_pr1(x3)
        print("3D | PR-1 (residual, strength=0) rel-L2:", float(_rel_l2(y3_pr1, x3)))

        layer3_pr2 = DWTSelfAttention3D(levels=2, wave='haar', strength=1.0,
                                        use_orient_mix=False, dwt_compute_dtype='float32',
                                        heads=2, key_dim=8)
        _ = layer3_pr2(x3)
        layer3_pr2.alpha_hp.assign(0.0); layer3_pr2.alpha_lp.assign(0.0)
        y3_pr2 = layer3_pr2(x3)
        print("3D | PR-2 (transform round-trip) rel-L2:", float(_rel_l2(y3_pr2, x3)))

        layer3 = DWTSelfAttention3D(levels=2, wave='haar', heads=2, key_dim=8)
        y3 = layer3(x3)
        print("3D | default strength rel-L2:", float(_rel_l2(y3, x3)))

        model3 = keras.Sequential([keras.Input((D3, D3, D3, C)), layer3, keras.layers.Conv3D(C, 1)])
        model3.compile(optimizer='adam', loss='mse', jit_compile=False)
        model3.summary()
        model3.fit(tf.random.normal((1, D3, D3, D3, C)),
                   tf.random.normal((1, D3, D3, D3, C)),
                   epochs=1, verbose=1)

    print("\nDone.")
