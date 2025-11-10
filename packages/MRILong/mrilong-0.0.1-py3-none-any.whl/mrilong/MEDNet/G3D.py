# include ../dirx 
# mylibpath = [
#     '/home/IITB/vikram-gadre-r-and-d-group/kkt.ai/src/utils'
#     ]

# import sys
# [sys.path.insert(0,_) for _ in mylibpath]
# del mylibpath
# from ZScoreNormalize import ZScoreNormalize 
from MEDNet.utils.ZscoreNormalizeND import ZScoreNormalize
from MEDNet.utils.DiceLossND import DiceLoss
from MEDNet.utils.DiceMetricND import Dice
# from tf_nd_utils.WeightedSparseCategoricalCrossentropy import WeightedSparseCategoricalCrossentropy 
# from tf_nd_utils.RepeatChannelsLayerND import BlockRepeatAndConcat, BandIsolatedHPFusion # as RepeatChannelsLayer

from MEDNet.attentions.DWTSelfAttentionND import DWTSelfAttention3D
from MEDNet.attentions.WaveletViTND import OrientationMix


#%% rational conv (one filter in both conv2D and conv3Dtranspose)
import tensorflow as tf
from tensorflow.keras.layers import Conv3D, BatchNormalization, Activation, Dropout, MaxPool3D, Concatenate
from keras.layers import Conv3DTranspose
from TFDWT.DWT3DFB import DWT3D, IDWT3D
from keras import regularizers
from tensorflow.keras import constraints

# class RepeatChannelsLayer(tf.keras.layers.Layer):
#     def __init__(self, repeat_count=5, **kwargs):
#         super(RepeatChannelsLayer, self).__init__(**kwargs)
#         self.repeat_count = repeat_count

#     def call(self, inputs):
#         # inputs shape: (batch, N, N, 7)
#         # Split into 3 single-channel tensors
#         channels = tf.split(inputs, num_or_size_splits=7, axis=-1)

#         # Repeat each channel 'repeat_count' times along the channel dimension
#         repeated = [tf.repeat(ch, repeats=self.repeat_count, axis=-1) for ch in channels]

#         # Concatenate repeated channels along the channel axis
#         output = tf.concat(repeated, axis=-1)
#         return output


#%% filter numbers
configs = {
    '1234': (2,4,8,16),
    '2345': (4,8,16,32),
    '3456': (8, 16, 32, 64),
    '4567': (16, 32, 64, 128),  #new 
    '5678': (32, 64, 128, 256), #new 
}


#%%
@tf.keras.utils.register_keras_serializable(package="G3D")
class BandIsolatedHPFusion(tf.keras.layers.Layer):
    """
    Trainable, band-isolated fusion to prepare inputs for IDWT.
    - Keeps LH/HL/HH (3D: the 7 HP subbands) isolated; no mixing across bands.
    - Learns per-(band, channel) gains to expand HP bands to match the C channels of the lowpass.
    Inputs:
      [x, h] where
        x: (..., C)
        h: (..., B)   or (..., B*C) with B=7 (3D), 3 (2D)
    Output:
      concat([x, h_expanded]) with shape (..., C + B*C)
    """
    def __init__(self, bands: int = 7, nonneg: bool = True, epsilon: float = 0.05,
                 use_cross_band: bool = False, name=None, **kwargs):
        super().__init__(name=name, **kwargs)
        self.bands = int(bands)
        self.nonneg = bool(nonneg)
        self.epsilon = float(epsilon)
        self.use_cross_band = bool(use_cross_band)
        self._C = None

    def build(self, input_shapes):
        x_shape, h_shape = input_shapes
        self._C = int(x_shape[-1])
        # gains per (band, channel)
        init = tf.keras.initializers.Constant(0.541)  # softplus(0.541) ≈ 1.0
        self.gains = self.add_weight(
            name='gains', shape=(self.bands, self._C), initializer=init, trainable=True
        )
        # Optional per-band 1x1 projection to mix channels within each band (keeps band isolation)
        self.bandwise_proj = tf.keras.layers.Conv3D(
            filters=self.bands * self._C,
            kernel_size=1,
            padding='same',
            groups=self.bands,
            name=f"{self.name or 'bif'}_bandwise_pw1"
        )
        # Optional residual cross-band projection (disabled by default)
        if self.use_cross_band:
            self.cross_band_proj = tf.keras.layers.Conv3D(
                filters=self.bands * self._C,
                kernel_size=1,
                padding='same',
                groups=self._C,
                kernel_initializer='he_normal',  # start as no-op
                bias_initializer='zeros',
                name=f"{self.name or 'bif'}_crossband_pw1"
            )
        else:
            self.cross_band_proj = None
        super().build(input_shapes)

    def call(self, inputs):
        x, h = inputs  # x: (..., C), h: (..., B) or (..., B*C)
        C = tf.shape(x)[-1]
        B = self.bands

        # shape-normalize h -> (..., B, C)
        h_shape = tf.shape(h)
        last = h_shape[-1]

        def _reshape_h():
            return tf.reshape(h, tf.concat([h_shape[:-1], [B, C]], axis=0))

        def _broadcast_h():
            return tf.broadcast_to(tf.expand_dims(h, axis=-1), tf.concat([h_shape, [C]], axis=0))

        h_bc = tf.cond(tf.equal(last, B), _broadcast_h, _reshape_h)  # (..., B, C)

        gains = self.gains
        if self.nonneg:
            gains = tf.nn.softplus(gains) + self.epsilon
        h_weighted = h_bc * gains  # (..., B, C)

        # flatten bands into channels: (..., B*C)
        h_flat = tf.reshape(h_weighted, tf.concat([tf.shape(h_weighted)[:-2], [B * C]], axis=0))
        # per-band projection (groups=B) then optional cross-band residual (groups=C)
        h_iso = self.bandwise_proj(h_flat)
        if self.cross_band_proj is not None:
            h_cb  = self.cross_band_proj(h_iso)
            h_proj = h_iso + h_cb
        else:
            h_proj = h_iso

        return tf.concat([x, h_proj], axis=-1)

    def get_config(self):
        cfg = super().get_config()
        cfg.update({
            'bands': self.bands,
            'nonneg': self.nonneg,
            'epsilon': self.epsilon,
            'use_cross_band': self.use_cross_band
        })
        return cfg



@tf.keras.utils.register_keras_serializable(package="G3D")
class ConvexBlend(tf.keras.layers.Layer):
    """Learn a normalized two-term convex (or near-convex) blend of two tensors.

    Given inputs [x_prev, x_new], outputs
        y = (w_prev * x_prev + w_new * x_new) / (w_prev + w_new + eps)
    where w_prev = softplus(a), w_new = softplus(b) so weights are non-negative.

    Broadcasting along channel dim is preserved (e.g., shapes (...,C) and (...,1)).
    Initialize a=b=0 → softplus(0)=~0.693 so initial blend ≈ equal 0.5/0.5.
    """
    def __init__(self, init_prev=0.0, init_new=0.0, epsilon=1e-6, name=None, **kw):
        super().__init__(name=name, **kw)
        self.init_prev = float(init_prev)
        self.init_new  = float(init_new)
        self.epsilon   = float(epsilon)
    def build(self, input_shapes):
        self.a_prev = self.add_weight(
            name="a_prev", shape=(), initializer=tf.keras.initializers.Constant(self.init_prev), trainable=True
        )
        self.a_new = self.add_weight(
            name="a_new", shape=(), initializer=tf.keras.initializers.Constant(self.init_new), trainable=True
        )
        super().build(input_shapes)
    def call(self, inputs):
        x_prev, x_new = inputs
        w_prev = tf.nn.softplus(self.a_prev)
        w_new  = tf.nn.softplus(self.a_new)
        denom = w_prev + w_new + self.epsilon
        return (w_prev * x_prev + w_new * x_new) / denom
    def get_config(self):
        return {**super().get_config(),
                'init_prev': self.init_prev,
                'init_new': self.init_new,
                'epsilon': self.epsilon}



@tf.keras.utils.register_keras_serializable(package="G3D")
class SEBandGate3D(tf.keras.layers.Layer):
    """
    Band-isolated squeeze-excitation over the 7 high-pass bands.
    Inputs: [lp, hp] with hp shape [..., 7*C]; output has the same shape as hp.
    Uses GAP(lp) -> Dense(7) -> softplus -> per-band scaling of hp.
    """
    def __init__(self, bands=7, init=0.541, name=None, **kw):
        """init ~ 0.541 so softplus(init) ≈ 1.0 (unity start)."""
        super().__init__(name=name, **kw)
        self.bands = int(bands)
        self.init = float(init)
        # keep spatial dims so subsequent 1x1x1 Conv3D can replace Dense safely
        self.gap = tf.keras.layers.GlobalAveragePooling3D(keepdims=True)
        # Use 1x1x1 conv instead of Dense to remain fully conv and size-agnostic
        self.conv = tf.keras.layers.Conv3D(
            filters=self.bands, kernel_size=1, padding="same",
            kernel_initializer="zeros",
            bias_initializer=tf.keras.initializers.Constant(self.init),
            name=f"{name or 'se_band'}_conv1x1"
        )
    def call(self, inputs):
        # Support [lp, hp] or [lp, hp, ctx]; ignore ctx for simplified gate
        if isinstance(inputs, (list, tuple)):
            lp, hp = inputs[0], inputs[1]
        else:
            lp, hp = inputs
        pooled = self.gap(lp)
        # w: [B,1,1,1,7]
        w = tf.nn.softplus(self.conv(pooled))
        B = tf.shape(hp)[0]; D=tf.shape(hp)[1]; H=tf.shape(hp)[2]; W=tf.shape(hp)[3]
        C = tf.shape(hp)[-1] // self.bands
        hp6 = tf.reshape(hp, [B, D, H, W, self.bands, C])      # [...,7,C]
        w6  = w[:, :, :, :, :, None]                           # [B,1,1,1,7,1]
        hpG = hp6 * w6
        return tf.reshape(hpG, [B, D, H, W, self.bands * C])
    def build(self, input_shapes):
        # input_shapes: [lp_shape, hp_shape] or [lp_shape, hp_shape, ctx_shape]
        if isinstance(input_shapes, (list, tuple)) and len(input_shapes) >= 1:
            lp_shape = input_shapes[0]
        else:
            lp_shape = input_shapes
        self.gap.build(lp_shape)
        c = int(lp_shape[-1]) if lp_shape[-1] is not None else None
        self.conv.build((None, 1, 1, 1, c))
        super().build(input_shapes)
    def get_config(self):
        return {**super().get_config(), "bands": self.bands, "init": self.init}

@tf.keras.utils.register_keras_serializable(package="G3D")
class ChannelSelector3D(tf.keras.layers.Layer):
    """Per-channel gates (SE-style) and optional reduction via 1x1x1 conv."""
    def __init__(self, keep_ratio=1.0, min_channels=1, gate_init=0.0, name=None, **kw):
        super().__init__(name=name, **kw)
        self.keep_ratio  = float(keep_ratio)
        self.min_channels = int(min_channels)
        self.gate_init = float(gate_init)
        # keep spatial dims for conv-based gating
        self._gap  = tf.keras.layers.GlobalAveragePooling3D(keepdims=True)
        self._gate = None
        self._proj = None
    def build(self, input_shape):
        C = int(input_shape[-1])
        # 1x1x1 conv to generate per-channel gates
        self._gate = tf.keras.layers.Conv3D(
            filters=C, kernel_size=1, padding="same",
            kernel_initializer="zeros",
            bias_initializer=tf.keras.initializers.Constant(self.gate_init),
            name=f"{self.name}_gate1x1"
        )
        if self.keep_ratio < 0.9999:
            k = max(self.min_channels, int(round(C * self.keep_ratio)))
            self._proj = tf.keras.layers.Conv3D(k, 1, padding="same",
                                                kernel_initializer="he_normal",
                                                use_bias=True, name=f"{self.name}_proj")
        super().build(input_shape)
    def call(self, x):
        a = self._gate(self._gap(x))         # [B,1,1,1,C]
        g = tf.nn.softplus(a)                # (0, ∞)
        xg = x * g                           # broadcast
        return self._proj(xg) if self._proj is not None else xg
    def get_config(self):
        cfg = super().get_config()
        cfg.update({
            'keep_ratio': self.keep_ratio,
            'min_channels': self.min_channels,
            'gate_init': self.gate_init,
        })
        return cfg

@tf.keras.utils.register_keras_serializable(package="G3D")
class ChannelAffine1x1(tf.keras.layers.Layer):
    """Per-channel identity-initialized scaling: y = x * (1 + gamma).

    Acts like a depthwise 1x1x1 conv initialized to identity, with optional L2
    regularization encouraging minimal deviation (wavelet refinement hook).
    """
    def __init__(self, l2_strength=1e-5, name=None, **kw):
        super().__init__(name=name, **kw)
        self.l2_strength = float(l2_strength)
        self._gamma = None
    def build(self, input_shape):
        C = int(input_shape[-1]) if input_shape[-1] is not None else None
        if C is None:
            raise ValueError("ChannelAffine1x1 requires known channel dimension at build time.")
        self._gamma = self.add_weight(
            name="gamma", shape=(C,), initializer="zeros", trainable=True,
            regularizer=tf.keras.regularizers.L2(self.l2_strength) if self.l2_strength > 0 else None
        )
        super().build(input_shape)
    def call(self, x):
        gamma = tf.cast(self._gamma, x.dtype)
        return x * (1.0 + gamma)
    def get_config(self):
        return {**super().get_config(), 'l2_strength': self.l2_strength}



#%%
def default_conv(f, x, activation='relu',  Ψ='haar'):
    padding = 'same'#'valid'
    x = Conv3D(filters=f, 
        kernel_size=3, 
        # kernel_regularizer=wL1L2Regularizer(l1=1e-5, l2=1e-4, Ψ=Ψ), 
        padding=padding)(x)
    # x = BatchNormalization()(x)
    # x = Activation(activation)(x)
    # x = Dropout(0.1)(x)
    x = Conv3D(filters=f, 
        kernel_size=3,
        # kernel_regularizer=wL1L2Regularizer(l1=1e-5, l2=1e-4, Ψ=Ψ),  
        padding=padding)(x)
    # x = BatchNormalization()(x)
    x = Activation(activation)(x)
    return x

# def default_upsample(filters, x, activation='relu'):
#     return Conv3DTranspose(filters, (2, 2, 2), strides=(2, 2, 2), padding='same')(x)

def default_upsample(x, activation='relu'):
    """Upsample by 2 using Conv3DTranspose.

    The output number of filters matches the input tensor's channel count when
    known; this lets the upsample operation preserve channel dimensionality and
    avoids needing an explicit `filters` argument.
    """
    # in_ch = x.shape[-1]
    # out_filters = int(in_ch) if in_ch is not None else 1
    y = Conv3DTranspose(x.shape[-1]//2, (2, 2, 2), strides=(2, 2, 2), padding='same')(x)
    if activation:
        y = Activation(activation)(y)
    return y


def default_pooling(q):
    return tf.keras.layers.MaxPool3D(pool_size=(2, 2, 2))(q)

def mix1x1(f, x, activation='relu'):
    """Lightweight 1x1x1 channel mixer used in decoder hops."""
    y = Conv3D(filters=f, kernel_size=1, padding='same')(x)
    if activation:
        y = Activation(activation)(y)
    return y

def mix_sep_res(f, x, activation='swish', name=None, use_norm=False, dropout_rate=0.0):
    """Separable residual mixer: depthwise 3x3x3 (groups=C) + pointwise 1x1x1 with residual.

    Enhancements (#4, #5): optional LayerNorm and tiny dropout for stability.
    If input channels != f, a 1x1x1 projection aligns the residual.
    """
    C = x.shape[-1]
    # Depthwise via grouped Conv3D (groups=C) when channel dim is known; otherwise fallback to regular conv
    if C is not None:
        y = Conv3D(filters=int(C), kernel_size=3, padding='same', groups=int(C), name=None if name is None else f"{name}_dw3")(x)
    else:
        y = Conv3D(filters=f, kernel_size=3, padding='same', name=None if name is None else f"{name}_dw3")(x)
    if use_norm:
        y = tf.keras.layers.LayerNormalization(epsilon=1e-5, name=None if name is None else f"{name}_ln1")(y)
    # Pointwise conv to mix channels
    y = Conv3D(filters=f, kernel_size=1, padding='same', name=None if name is None else f"{name}_pw1")(y)
    if use_norm:
        y = tf.keras.layers.LayerNormalization(epsilon=1e-5, name=None if name is None else f"{name}_ln2")(y)
    if dropout_rate and dropout_rate > 0:
        y = Dropout(dropout_rate, name=None if name is None else f"{name}_do")(y)
    # Residual connection (with projection if needed)
    if C is None or C != f:
        res = Conv3D(filters=f, kernel_size=1, padding='same', name=None if name is None else f"{name}_resproj")(x)
    else:
        res = x
    y = tf.keras.layers.Add(name=None if name is None else f"{name}_add")([res, y])
    if activation:
        y = Activation(activation, name=None if name is None else f"{name}_act")(y)
    return y

# def default_bottleneck(q):
#         return q
def default_bottleneck(x):
    return Conv3D(
        x.shape[-1], kernel_size=1, padding='same',
        kernel_regularizer=regularizers.L1L2(l1=1e-6, l2=1e-5),
        name="latent_layer"
    )(x)

#%%
def Gφψ3D(
    input_shape=(32, 32, 32, 1),
    config=(16, 32, 64, 128),   ## scope for # of filters
    n_classes=4,
    conv_fn=None,               ## scope for other convolutional systems
    pooling_fn=None,            ## scope for other downsampling systems
    unpool_fn=None,             ## scope for other upsampling systems
    bottleneck_fn=None,         ## scope for other bottleneck systems
    output_kernel_regularizer=None,
    one_hot_encode=True,
    residual=False,
    wavelet_refine=True,
    Ψ='haar'):
    """ A 3D Gφψ3D (MEDCNN)

        MEDNet: Multiresolution Encoder-Decoder Frugal Convolutional Neural Network.
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
        """
    """Deterministic G"""
    conv = conv_fn or default_conv
    pool = pooling_fn or default_pooling
    bottleneck = bottleneck_fn or default_bottleneck
    up = unpool_fn or default_upsample
    a, b, c, d  = config
    if output_kernel_regularizer is not None:
        output_kernel_regularizer = regularizers.L1L2(l1=1e-6, l2=1e-5)
    """system configs"""
      
    ## Wavelet Filterbank decomposition
    def wavelet_filter_bank(s, Ψ=Ψ):
        """DWT Level 4 decomposition with optional learnable pre-analysis scaling."""
        src = ChannelAffine1x1(name='aff_lvl1_pre')(s) if wavelet_refine else s
        lh = DWT3D(wave=Ψ)(src)
        l1 = lh[:, :, :, :, :1]; h1 = lh[:, :, :, :, 1:]
        # Level 2
        l1_in = ChannelAffine1x1(name='aff_lvl2_pre')(l1) if wavelet_refine else l1
        lh = DWT3D(wave=Ψ)(l1_in)
        l2 = lh[:, :, :, :, :1]; h2 = lh[:, :, :, :, 1:]
        # Level 3
        l2_in = ChannelAffine1x1(name='aff_lvl3_pre')(l2) if wavelet_refine else l2
        lh = DWT3D(wave=Ψ)(l2_in)
        l3 = lh[:, :, :, :, :1]; h3 = lh[:, :, :, :, 1:]
        # Level 4
        l3_in = ChannelAffine1x1(name='aff_lvl4_pre')(l3) if wavelet_refine else l3
        lh = DWT3D(wave=Ψ)(l3_in)
        l4 = lh[:, :, :, :, :1]; h4 = lh[:, :, :, :, 1:]
        return (l1, l2, l3, l4), (h1, h2, h3, h4)
    
        # ## ACTUAL DWT PYRAMID
        # subbands = [l1, h1, h2, h3, h4]
        # return subbands

        
    # lowpass, highpass = wavelet_filter_bank(s, Ψ)
    # l1, l2, l3, l4 = lowpass 
    # h1, h2, h3, h4 = highpass

    
    # def dwt_lowpass(x):
    #     """Decimate by DWT lowpass per-channel (no extra MaxPool)."""
    #     lx = DWT3D(wave=Ψ)(x)
    # # take the first Cx channels as lowpass of each channel
    # # tf.shape on a KerasTensor must be used inside a Keras layer; wrap in Lambda
    # pair = [lx, x]
    # return tf.keras.layers.Lambda(lambda t: t[0][..., :tf.shape(t[1])[-1]])(pair)
    @tf.keras.utils.register_keras_serializable(package="G3D")
    class DWTLowpass3D(tf.keras.layers.Layer):
        """Per-channel 3D DWT lowpass decimator without Lambda.

        Applies DWT3D and returns the first F channels where F is the input channel count,
        effectively selecting the lowpass subband per input channel.
        """
        def __init__(self, wave='haar', name=None, **kw):
            super().__init__(name=name, **kw)
            self.wave = wave
            # Instantiate underlying DWT as a tracked sublayer in __init__
            self._dwt = DWT3D(wave=self.wave)
        def build(self, input_shape):
            # Ensure sublayer is built within this layer's scope
            self._dwt.build(input_shape)
            super().build(input_shape)
        def call(self, x):
            y = self._dwt(x)  # shape [..., 8F]
            F = tf.shape(x)[-1]
            return y[..., :F]
        def get_config(self):
            return {**super().get_config(), 'wave': self.wave}

    def dwt_lowpass(x, wave=Ψ):
        """Decimate by DWT lowpass per-channel using a serializable Layer (no Lambda)."""
        return DWTLowpass3D(wave=wave)(x)

    def trainable_decimation_path(lowpass, config=(16, 32, 64, 128)):
        """Encoder lowpass path with dynamic convex blends at each scale merge."""
        l1, l2, l3, l4 = lowpass

        # Stage 1 (no prior merge; just process l1 then decimate)
        xl1_ = conv(a, l1)  # skip+1 (pre-decimation features at level 1)
        xl1 = dwt_lowpass(xl1_)  # -> size of l2

        # Stage 2 (blend previous processed lowpass with fresh raw lowpass l2)
        xl2 = ConvexBlend(name='lambda2_blend')([xl1, l2])
        xl2_ = conv(b, xl2)  # skip+2
        xl2d = dwt_lowpass(xl2_)  # -> size of l3

        # Stage 3
        xl3 = ConvexBlend(name='lambda3_blend')([xl2d, l3])
        xl3_ = conv(c, xl3)  # skip+3
        xl3d = dwt_lowpass(xl3_)  # -> size of l4

        # Stage 4
        xl4 = ConvexBlend(name='lambda4_blend')([xl3d, l4])
        xl4_ = conv(d, xl4)  # bottleneck pre-bottleneck conv

        return xl4_, (xl1_, xl2_, xl3_)


    def reconstruction_path(z, highpass, lfskips, kernel_size=3, padding='same'):
        # unpack HP subbands
        h1, h2, h3, h4 = highpass

        # use original encoder lowpass skips directly (no trainable upsampling)
        xl1_, xl2_, xl3_ = lfskips

        # Channel selection on bottleneck and skips
        # Neutral-ish gate init (~1.0 after softplus) and fixed output widths
        z    = ChannelSelector3D(keep_ratio=0.25, min_channels=c, gate_init=0.541, name="sel_z")(z)
        sel3 = ChannelSelector3D(keep_ratio=0.25, min_channels=c, gate_init=0.541, name="sel_skip_l3")(xl3_)
        sel2 = ChannelSelector3D(keep_ratio=0.25, min_channels=b, gate_init=0.541, name="sel_skip_l2")(xl2_)
        sel1 = ChannelSelector3D(keep_ratio=0.25, min_channels=a, gate_init=0.541, name="sel_skip_l1")(xl1_)

        # ---- IDWT-only hops (band-isolated with SE gating) ----
        # Hop 4 → l3 (simplified gate; no extra context)
        h4g = SEBandGate3D(name="h4_gate")([z, h4])
        # OrientationMix dropped at h4g for efficiency (kept only at h1g)
        h4g = OrientationMix(groups=7)(h4g)
        iw3 = IDWT3D(wave=Ψ, name="idwt_h4")(BandIsolatedHPFusion(use_cross_band=True, name="bif_h4")([z, h4g]))
        if wavelet_refine:
            iw3 = ChannelAffine1x1(name='aff_lvl4_post')(iw3)
        iw3 = mix_sep_res(c, Concatenate(name="l3_cat")([sel3, iw3]), name="mix_l3")

        # Hop 3 → l2 (simplified gate; no extra context)
        h3g = SEBandGate3D(init=0.7, name="h3_gate")([iw3, h3])
        h3g = OrientationMix(groups=7)(h3g)
        iw2 = IDWT3D(wave=Ψ, name="idwt_h3")(BandIsolatedHPFusion(use_cross_band=True, name="bif_h3")([iw3, h3g]))
        if wavelet_refine:
            iw2 = ChannelAffine1x1(name='aff_lvl3_post')(iw2)
        iw2 = mix_sep_res(b, Concatenate(name="l2_cat")([sel2, iw2]), name="mix_l2")

        # Hop 2 → l1 (slightly favor HP and allow cross-orientation at fine scale)
        h2g = SEBandGate3D(init=0.7, name="h2_gate")([iw2, h2])
        h2g = OrientationMix(groups=7)(h2g)
        iw1 = IDWT3D(wave=Ψ, name="idwt_h2")(BandIsolatedHPFusion(use_cross_band=True, name="bif_h2")([iw2, h2g]))
        if wavelet_refine:
            iw1 = ChannelAffine1x1(name='aff_lvl2_post')(iw1)
        iw1 = mix_sep_res(a, Concatenate(name="l1_cat")([sel1, iw1]), name="mix_l1")

        # Hop 1 → full res (simplified gate; no extra context)
        h1g = SEBandGate3D(init=0.7, name="h1_gate")([iw1, h1])
        h1g = OrientationMix(groups=7)(h1g)
        R = IDWT3D(wave=Ψ, name="idwt_h1")(BandIsolatedHPFusion(use_cross_band=True, name="bif_h1")([iw1, h1g]))
        if wavelet_refine:
            R = ChannelAffine1x1(name='aff_lvl1_post')(R)

        # Lightweight edge-aware residual at full resolution (minimal edit):
        # # Project h1g (HP) to match R channels, produce a per-channel scalar gate, and add to R.
        # edge = Conv3D(a, 1, padding='same', kernel_initializer='zeros', bias_initializer='zeros', name='edge_1x1')(h1g)
        # edge_gate = tf.keras.layers.GlobalAveragePooling3D(keepdims=True, name='edge_gap')(edge)
        # edge_gate = Activation('sigmoid', name='edge_gate')(edge_gate)
        # # match spatial size to R (full-res) before adding
        # edge_up = Conv3DTranspose(a, (2, 2, 2), strides=(2, 2, 2), padding='same', name='edge_up')(edge)
        # R = tf.keras.layers.Add(name='edge_bias_add')([R, edge_up * edge_gate])

        # Return both the reconstruction and the last gated HP for optional edge residuals
        return R, h1g

        

    # input_shape =(256, 256, 256, 1)
    inputs = tf.keras.layers.Input(input_shape)
    s = ZScoreNormalize()(inputs)
    s = DWTSelfAttention3D(levels=4, wave=Ψ, heads=2, key_dim=8)(s)
    lowpass, highpass = wavelet_filter_bank(s, Ψ)
    
    xl4_, lfskips = trainable_decimation_path(lowpass)
    z = bottleneck(xl4_) 
    R, h1g = reconstruction_path(z, highpass, lfskips)
   
    if residual==True:
        R = Concatenate()([s, R])

    if one_hot_encode==True: 
        last_activation = 'softmax'
    else: last_activation=None
    # Edge residual bypass removed (previously: edge_1x1 -> upsample -> scalar gate -> add)
    # Intent: simplify decoder; can be reintroduced behind a flag if needed.

    R = DWTSelfAttention3D(levels=4, wave=Ψ, heads=2, key_dim=8)(R)  # add self-attention module at full res
    outputs = Conv3D(
        n_classes, 
        (1, 1, 1),
        # kernel_regularizer=regularizers.L2(1e-4),
        kernel_regularizer=output_kernel_regularizer,
        # bias_regularizer=regularizers.L2(1e-4),
        # activity_regularizer=regularizers.L2(1e-5), 
        activation=last_activation
        # activation="sigmoid"
        )(R)

    return tf.keras.Model(inputs=[inputs], outputs=[outputs])

# Gφψ3D(input_shape=(128, 128, 128,1), residual=True).summary()
# Gφψ3D(input_shape=(128, 128, 128, 1), residual=False).summary()

#%%
# class Dice(tf.keras.metrics.Metric):
#     def __init__(self, target_class_id=None, name=None, **kwargs):
#         name = name or f"dice_class_{target_class_id}"
#         super().__init__(name=name, **kwargs)
#         self.target_class_id = target_class_id

#         self.loss_fn = tf.keras.losses.Dice(reduction='none')
#         self.dice_sum = self.add_weight(name="dice_sum", initializer="zeros")
#         self.count = self.add_weight(name="count", initializer="zeros")

#     def update_state(self, y_true, y_pred, sample_weight=None):
#         y_true_cls = y_true[..., self.target_class_id]
#         y_pred_cls = y_pred[..., self.target_class_id]

#         y_true_cls = tf.expand_dims(y_true_cls, axis=-1)
#         y_pred_cls = tf.expand_dims(y_pred_cls, axis=-1)

#         dice_loss = self.loss_fn(y_true_cls, y_pred_cls)
#         dice_score = 1.0 - dice_loss

#         self.dice_sum.assign_add(tf.reduce_mean(dice_score))
#         self.count.assign_add(1.0)

#     def result(self):
#         return self.dice_sum / (self.count + 1e-7)

#     def reset_states(self):
#         self.dice_sum.assign(0.0)
#         self.count.assign(0.0)


#%%


class G3D(tf.keras.Model):
    """ A concise Gφψ3D and UNet3D wrapper class 
    
        MEDNet: Multiresolution Encoder-Decoder Frugal Convolutional Neural Network.
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
    
    
    --kkt@18Jun2025 """
    def __init__(
        self, input_shape=(32, 32, 32, 1), 
        model=None,
        loss='focal', # or dice
        class_weights=0.25, #[0.1, 0.2, 0.3, 0.5],
        # config=(16, 32, 64, 128), 
        n_classes=4, 
        # conv_fn=None,               ## scope for other convolutional systems
        # pooling_fn=None,            ## scope for other downsampling systems
        # unpool_fn=None,
        # residual=False,        
        # Ψ='haar',
        *args, **kwargs):
        super().__init__(*args, **kwargs)       
        # self.input_shape = input_shape
        # self.config = config
        # self.n_classes = n_classes
        # self.residual = residual
        if model is not None:
            self.model = model
        else: raise ValueError("Error!! model=None \nfunctional model not available. \n")
        
        
        # self.model = Gφψ3D(
        #     input_shape=input_shape, 
        #     config=config, 
        #     n_classes=n_classes, 
        #     conv_fn=None,               ## scope for other convolutional systems
        #     pooling_fn=None,            ## scope for other downsampling systems
        #     unpool_fn=None,
        #     residual=residual,
        #     Ψ=Ψ
        #     )
        
        focal_loss = tf.keras.losses.CategoricalFocalCrossentropy(
                alpha=class_weights,
                gamma=2.0,)
        dice_loss = DiceLoss(class_weights=class_weights)
        sparse_loss = tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True)
        # sparse_loss = WeightedSparseCategoricalCrossentropy(class_weights, from_logits=True)

        if loss=='focal':
            self.loss = focal_loss
        elif loss=='dice':
            self.loss = dice_loss
        elif loss=='sparse':
            self.loss = sparse_loss            

        ## Metrics trackers
        # self.total_loss_tracker = tf.keras.metrics.Mean(name="total_loss")
        self.reconstruction_loss_tracker = tf.keras.metrics.Mean(name="reconstruction_loss")
        # self.kl_loss_tracker = tf.keras.metrics.Mean(name="kl_loss")

        ## IoU metrics for classes 1, 2, 3 (excluding background class 0)
        self.iou_metrics = {
            f'IoU_class_{i}': tf.keras.metrics.IoU(num_classes=n_classes, target_class_ids=[i])
            for i in range(n_classes)#[1, 2, 3]
        }
        # self.iou_metrics = {
        #     f'IoU_class_{i}': tf.keras.metrics.OneHotIoU(num_classes=n_classes, target_class_ids=[i])
        #     for i in [1, 2, 3]
        # }
        self.dice_metrics = {
            f'Dice_class_{i}': Dice(target_class_ids=[i])
            for i in range(n_classes)
        }
        # self.mean_iou = tf.keras.metrics.MeanIoU(num_classes=n_classes)

    
    @property
    def metrics(self):
        return [
            self.reconstruction_loss_tracker,
            # self.mean_iou,
            *self.iou_metrics.values(),
            *self.dice_metrics.values()
        ]

    def call(self, inputs, training=False):
        return self.model(inputs, training=training)

    def train_step(self, data):
        x, y_true = data

        with tf.GradientTape() as tape:
            # Forward pass
            y_pred = self(x, training=True)
            loss = self.loss(y_true, y_pred)  
            # loss = self.dice(y_true, y_pred)   

        grads = tape.gradient(loss, self.trainable_weights)
        self.optimizer.apply_gradients(zip(grads, self.trainable_weights))
        # grads = tape.gradient(total_loss, self.trainable_variables)
        # self.optimizer.apply_gradients(zip(grads, self.trainable_variables))

        # self.total_loss_tracker.update_state(total_loss)
        self.reconstruction_loss_tracker.update_state(loss)
        # self.kl_loss_tracker.update_state(kl_loss)

        # Convert predictions to class indices for IoU
        y_true_class = tf.argmax(y_true, axis=-1)
        y_pred_class = tf.argmax(y_pred, axis=-1)
        
        # Update IoU metrics
        for metric in self.iou_metrics.values():
            metric.update_state(y_true_class, y_pred_class)
        # self.mean_iou.update_state(y_true_class, y_pred_class)

        for metric in self.dice_metrics.values():
            metric.update_state(y_true, y_pred)

        results = {
            "loss": self.reconstruction_loss_tracker.result(),
            # "mean_IoU": self.mean_iou.result(),
            **{name: metric.result() for name, metric in self.iou_metrics.items()},
            **{name: metric.result() for name, metric in self.dice_metrics.items()}
        }
        # Add individual IoU metrics
        # results.update({name: metric.result() for name, metric in self.iou_metrics.items()})
        return results

    def test_step(self, data):
        x, y_true = data
        y_pred = self(x, training=False)
        loss = self.loss(y_true, y_pred)
        self.reconstruction_loss_tracker.update_state(loss)

        y_true_class = tf.argmax(y_true, axis=-1)
        y_pred_class = tf.argmax(y_pred, axis=-1)

        for metric in self.iou_metrics.values():
            metric.update_state(y_true_class, y_pred_class)
        # self.mean_iou.update_state(y_true_class, y_pred_class)

        for metric in self.dice_metrics.values():
            metric.update_state(y_true, y_pred)

        results = {
            "loss": self.reconstruction_loss_tracker.result(),
            # "mean_IoU": self.mean_iou.result(),
            **{name: metric.result() for name, metric in self.iou_metrics.items()},
            **{name: metric.result() for name, metric in self.dice_metrics.items()}
        }
        return results

if __name__=='__main__':

    n = 32
    input_shape = (n,n,n,1)
    # config=(16, 32, 64, 128), 
    n_classes=4
    # conv_fn=None,               ## scope for other convolutional systems
    # pooling_fn=None,            ## scope for other downsampling systems
    # unpool_fn=None,
    residual=False,
    G = Gφψ3D(
        input_shape=input_shape, 
        # config=config, 
        n_classes=n_classes, 
        conv_fn=None,               ## scope for other convolutional systems
        pooling_fn=None,            ## scope for other downsampling systems
        unpool_fn=None,
        residual=residual,
        Ψ='haar'
        )
    
    
    # model = G3D(input_shape=(n,n,n,1), loss='focal', class_weights=[0.1, 0.2, 0.3, 0.5], residual=True)
    model = G3D(input_shape=(n,n,n,1), model=G,  loss='dice', class_weights=[0.1, 0.2, 0.3, 0.5])
    # model.build(input_shape=(None, n, n, n, 1))
    model.compile(optimizer=tf.keras.optimizers.Adam(1e-4))
    model.summary()

    ## Sample train
    X_train = tf.random.normal((2, n, n, n, 1))
    Y_train = tf.random.uniform((2, n, n, n, 4))
    
    train_dataset = tf.data.Dataset.from_tensor_slices((X_train, Y_train)).batch(2)

    model.fit(train_dataset, epochs=5)
