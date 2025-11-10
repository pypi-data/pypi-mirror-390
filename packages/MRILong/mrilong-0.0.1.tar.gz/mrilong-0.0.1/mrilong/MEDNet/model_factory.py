"""
Model Factory for 3D Brain Segmentation
---------------------------------------
Centralizes model creation for MEDNet 3D architectures.

It prefers the MEDNet package (renamed from MEDNet_nightly).
"""

import os
 
import tensorflow as tf
Gφψ3D_ViT = None  # default if not available; prefer nightly import below

# Prefer renamed stable package (formerly MEDNet_nightly)
from MEDNet.G3D import Gφψ3D, G3D, configs
from MEDNet.UNet3D import UNet3D
try:
    from MEDNet.UNet3Ddwtattn import UNet3Ddwtattn  # optional
except Exception:
    UNet3Ddwtattn = None  # type: ignore
try:
    from MEDNet.UNet3Dattention import UNet3D_with_attention as UNet3Dattention  # optional
except Exception:
    UNet3Dattention = None  # type: ignore
try:
    from MEDNet.G3Dattention import Gφψ3D_attention as G3Dattention  # optional
except Exception:
    G3Dattention = None  # type: ignore
try:
    from MEDNet.UNet3DViT import UNet3DViT  # optional
except Exception:  # pragma: no cover - optional
    UNet3DViT = None  # type: ignore
try:
    from MEDNet.G3DViT import Gφψ3D_ViT  # optional
except Exception:  # pragma: no cover - optional
    Gφψ3D_ViT = None  # type: ignore
try:
    from MEDNet.G3DwaveViT import Gφψ3D_waveViT  # optional
except Exception:  # pragma: no cover - optional
    Gφψ3D_waveViT = None  # type: ignore
try:
    # Module renamed: FDSTUNet3D.py -> ShearMEDNet3D.py; factory keeps the same symbol name
    from MEDNet.ShearMEDNet3D import FDSTUNet3D  # optional
except Exception:  # pragma: no cover - optional
    FDSTUNet3D = None  # type: ignore
try:
    # New: ShearMED UNet with FDST-native ViT bottleneck (deterministic)
    from MEDNet.ShearMEDFDSTViTNet3D import ShearMEDFDSTViTNet3D  # optional
except Exception as _e:  # pragma: no cover - optional
    print("[model_factory] ShearMEDFDSTViTNet3D import failed:", type(_e).__name__, _e)
    ShearMEDFDSTViTNet3D = None  # type: ignore
try:
    # Module renamed: FDSTCVAEUNet3D.py -> CVShearMEDNet3D.py; factory keeps the same symbol name
    from MEDNet.CVShearMEDNet3D import FDSTCVAEUNet3D  # optional
except Exception:  # pragma: no cover - optional
    FDSTCVAEUNet3D = None  # type: ignore
try:
    # Renamed: FDSTCVAEUNetWaveViT3D.py -> CVShearMEDWaveViTNet3D.py; export alias provided
    from MEDNet.CVShearMEDWaveViTNet3D import CVShearMEDWaveViTNet3D  # optional
except Exception as _e:  # pragma: no cover - optional
    print("[model_factory] CVShearMEDWaveViTNet3D import failed:", type(_e).__name__, _e)
    CVShearMEDWaveViTNet3D = None  # type: ignore
try:
    from MEDNet.G3DLifting import Gφψ3D as Gφψ3D_Lifting  # optional
except Exception:  # pragma: no cover - optional
    Gφψ3D_Lifting = None  # type: ignore
try:
    from MEDNet.G3D_minimal import Gφψ3D as Gφψ3D_Minimal  # optional
except Exception:  # pragma: no cover - optional
    Gφψ3D_Minimal = None  # type: ignore
try:
    # Module was renamed from CVAEUNet3D.py to CVUNet3D.py; class name unchanged
    from MEDNet.CVUNet3D import CVAEUNet3D  # optional
except Exception as _e:  # pragma: no cover - optional
    print("[model_factory] CVAEUNet3D import failed:", type(_e).__name__, _e)
    CVAEUNet3D = None  # type: ignore
try:
    # Use the new, single source of truth
    from MEDNet.CVUWaveViTNet3D import CVUWaveViTNet3D  # optional
except Exception as _e:  # pragma: no cover - optional
    print("[model_factory] CVUWaveViTNet3D import failed:", type(_e).__name__, _e)
    CVUWaveViTNet3D = None  # type: ignore
try:
    # New ShearMED UNet variant with FDSTViT VAE bottleneck
    from MEDNet.CVShearMEDFDSTViTNet3D import FDSTCVAEUNetFDSTViT3D  # optional
except Exception as _e:  # pragma: no cover - optional
    print("[model_factory] CVShearMEDFDSTViTNet3D import failed:", type(_e).__name__, _e)
    FDSTCVAEUNetFDSTViT3D = None  # type: ignore
try:
    # New UNet with FDSTViT VAE bottleneck (coefficient-domain)
    # Module renamed: CVAEUNetFDSTViT3D.py -> CVUFDSTViTNet3D.py (use the canonical exported alias)
    from MEDNet.CVUFDSTViTNet3D import CVUFDSTViTNet3D  # optional
except Exception as _e:  # pragma: no cover - optional
    print("[model_factory] CVUFDSTViTNet3D import failed:", type(_e).__name__, _e)
    CVUFDSTViTNet3D = None  # type: ignore
try:
    # Deterministic UNet with WaveletViT 3D bottleneck (feature-return)
    from MEDNet.UWaveViTNet3D import UNetWaveViT3D  # optional
except Exception as _e:  # pragma: no cover - optional
    print("[model_factory] UNetWaveViTNet3D import failed:", type(_e).__name__, _e)
    UNetWaveViT3D = None  # type: ignore
try:
    # Hybrid: IIR DF-II conv blocks + WaveletViT 3D bottleneck (deterministic)
    from MEDNet.UIIRDFIIWaveViTNet3D import UIIRDFIIWaveViTNet3D  # optional
except Exception as _e:  # pragma: no cover - optional
    print("[model_factory] UIIRDFIIWaveViTNet3D import failed:", type(_e).__name__, _e)
    UIIRDFIIWaveViTNet3D = None  # type: ignore
try:
    # Use the new DF-II separable IIR UNet variant (module renamed)
    from MEDNet.UIIRDFIINet3D import UIIRDFIINet3D as UIIRNet3D  # optional alias
except Exception as _e:  # pragma: no cover - optional
    print("[model_factory] UIIRDFIINet3D import failed:", type(_e).__name__, _e)
    UIIRNet3D = None  # type: ignore
try:
    from MEDNet.G3DIIRWaveViT import Gφψ3D_iirWaveViT  # optional
except Exception as _e:  # pragma: no cover - optional
    print("[model_factory] G3DIIRWaveViT import failed:", type(_e).__name__, _e)
    Gφψ3D_iirWaveViT = None  # type: ignore
from MEDNet.conv_systems.vanilla_conv import default_conv_block as _default_conv_block
from MEDNet.bottlenecks.vanilla_bottleneck import default_bottleneck as _default_bottleneck

# =============================================================================
# Model Configurations
# =============================================================================

# Config dictionary for different model configurations
configs = configs or {  # type: ignore[name-defined]
    '4567': (16, 32, 64, 128),
}

COMPONENT_REGISTRY = {
    'vanilla_conv': _default_conv_block,
    'vanilla_bottleneck': _default_bottleneck,
}

def get_conv_fn(conv_type):
    """Get convolution function by type"""
    if conv_type not in COMPONENT_REGISTRY:
        raise ValueError(f"Unknown conv_type: {conv_type}. Available: {list(COMPONENT_REGISTRY.keys())}")
    return COMPONENT_REGISTRY[conv_type]

def get_bottleneck_fn(bottleneck_type):
    """Get bottleneck function by type"""
    if bottleneck_type not in COMPONENT_REGISTRY:
        raise ValueError(f"Unknown bottleneck_type: {bottleneck_type}. Available: {list(COMPONENT_REGISTRY.keys())}")
    return COMPONENT_REGISTRY[bottleneck_type]

# =============================================================================
# Model Configurations
# =============================================================================

MODEL_CONFIGS = {
    'G': {
        'name': 'G3D',
        'description': 'G3D model with focal loss for 3D brain segmentation',
        'n_classes': 4,
        'loss': 'focal',
        'config_key': '4567',
        'conv_fn': 'vanilla_conv',
        'bottleneck_fn': 'vanilla_bottleneck'
    },
    'U': {
        'name': 'UNet3D',
        'description': 'UNet3D model with focal loss for 3D brain segmentation',
        'n_classes': 4,
        'loss': 'focal',
        'config_key': '4567',
        'conv_fn': 'vanilla_conv',
        'bottleneck_fn': 'vanilla_bottleneck'
    },
    'ufdstvitnet': {
        'name': 'UFDSTViTNet3D',
        'description': 'UFDSTViTNet3D with deterministic FDST-native ViT bottleneck (no VAE)',
        'n_classes': 4,
        'loss': 'focal',
        'config_key': '4567',
        'conv_fn': 'vanilla_conv',
        'bottleneck_fn': 'vanilla_bottleneck'
    },
    # ViT-backed U-Net
    'uvit': {
        'name': 'UNet3DViT',
        'description': 'UNet3D with Vision Transformer bottleneck',
        'n_classes': 4,
        'loss': 'focal',
        'config_key': '4567',
        'conv_fn': 'vanilla_conv',
    },
    # ViT-backed G3D
    'gvit': {
        'name': 'G3DViT',
        'description': 'G3D with Vision Transformer bottleneck',
        'n_classes': 4,
        'loss': 'focal',
        'config_key': '4567',
        'conv_fn': 'vanilla_conv',
    },
    # Attention U-Net
    'uattn': {
        'name': 'UNet3Dattention',
        'description': 'UNet3D with attention gates on skip connections',
        'n_classes': 4,
        'loss': 'focal',
        'config_key': '4567',
        'conv_fn': 'vanilla_conv',
        'bottleneck_fn': 'vanilla_bottleneck'
    },
    # Attention G3D
    'gattn': {
        'name': 'G3Dattention',
        'description': 'G3D with attention gates on skip connections',
        'n_classes': 4,
        'loss': 'focal',
        'config_key': '4567',
        'conv_fn': 'vanilla_conv',
        'bottleneck_fn': 'vanilla_bottleneck'
    },
    # DWT Attention U-Net
    'udwtattn': {
        'name': 'UNet3Ddwtattn',
        'description': 'UNet3D with DWT self-attention',
        'n_classes': 4,
        'loss': 'focal',
        'config_key': '4567',
        'conv_fn': 'vanilla_conv',
        'bottleneck_fn': 'vanilla_bottleneck'
    },
    # Wavelet-native ViT G3D
    'gwavevit': {
        'name': 'G3DwaveViT',
        'description': 'G3D with wavelet-native ViT bottleneck',
        'n_classes': 4,
        'loss': 'focal',
        'config_key': '4567',
        'conv_fn': 'vanilla_conv',
    },
    # FDST-based UNet3D (renamed from 'fdstunet' -> 'shearnet' -> 'shearmednet')
    'shearmednet': {
        'name': 'FDSTUNet3D',
        'description': 'UNet3D with Fast Discrete Shearlet Transform features',
        'n_classes': 4,
        'loss': 'focal',
        'config_key': '4567',
        'conv_fn': 'vanilla_conv',
        'bottleneck_fn': 'vanilla_bottleneck'
    },
    # ShearMED UNet with deterministic FDST-native ViT bottleneck
    'shearmedfdstvitnet': {
        'name': 'ShearMEDFDSTViTNet3D',
        'description': 'ShearMED UNet with FDST-native ViT bottleneck (no VAE, coef-domain)',
        'n_classes': 4,
        'loss': 'focal',
        'config_key': '4567',
        'conv_fn': 'vanilla_conv',
        'bottleneck_fn': 'vanilla_bottleneck'
    },
    # FDST-based UNet3D with CVAE bottleneck
    'cvshearmednet': {
        'name': 'CVShearMEDNet3D',
        'description': 'FDST-UNet with a CVAE bottleneck at the center',
        'n_classes': 4,
        'loss': 'focal',
        'config_key': '4567',
        'conv_fn': 'vanilla_conv',
        'bottleneck_fn': 'vanilla_bottleneck'
    },
    # FDST-based UNet3D with WaveViT VAE bottleneck
    'cvshearmedwavevitnet': {
        'name': 'CVShearMEDWaveViTNet3D',
        'description': 'FDST-UNet with WaveViT VAE bottleneck (μ/logσ² over tokens)',
        'n_classes': 4,
        'loss': 'focal',
        'config_key': '4567',
        'conv_fn': 'vanilla_conv',
        'bottleneck_fn': 'vanilla_bottleneck'
    },
        
    # G3D Lifting with DWT self-attention
    'glifting': {
        'name': 'G3DLifting',
        'description': 'G3D with lifting scheme and DWT self-attention at full resolution',
        'n_classes': 4,
        'loss': 'focal',
        'config_key': '4567',
        'conv_fn': 'vanilla_conv',
        'bottleneck_fn': 'vanilla_bottleneck'
    }
    ,
    # Minimal G3D variant (direct DWT-based UNet-like)
    'gminimal': {
        'name': 'G3D_minimal',
        'description': 'Minimal G3D (DWT3D/IDWT3D) baseline',
        'n_classes': 4,
        'loss': 'focal',
        'config_key': '4567',
        'conv_fn': 'vanilla_conv',
        'bottleneck_fn': 'vanilla_bottleneck'
    }
    ,
    # CVAE U-Net (self-contained wrapper)
    'cvunet': {
        'name': 'CVAEUNet3D',
        'description': 'Self-contained CVAE U-Net (KL + focal) built from Encoder/Decoder',
        'n_classes': 4,
        'loss': 'focal',
        'config_key': '4567',
        'conv_fn': 'vanilla_conv',
        'bottleneck_fn': 'vanilla_bottleneck'
    }
    ,
    # CVAE UNet with WaveViT bottleneck
    'cvuwavevitnet': {
        'name': 'CVUWaveViTNet3D',
        'description': 'UNet3D with WaveViT CV bottleneck (mu/logvar over tokens)',
        'n_classes': 4,
        'loss': 'focal',
        'config_key': '4567',
        'conv_fn': 'vanilla_conv',
    }
    ,
    # ShearMED UNet with FDSTViT VAE bottleneck (coefficient-domain)
    'cvshearmedfdstvitnet': {
        'name': 'CVShearMEDFDSTViTNet3D',
        'description': 'ShearMED UNet with FDSTViT VAE bottleneck (coef-domain, token/feature modes)',
        'n_classes': 4,
        'loss': 'focal',
        'config_key': '4567',
        'conv_fn': 'vanilla_conv',
    }
    ,
    # CVAE UNet with FDSTViT (coefficient-domain) bottleneck
    'cvufdstvitnet': {
        'name': 'CVUFDSTViTNet3D',
        'description': 'UNet3D with FDSTViT VAE bottleneck (coef-domain, z fused into features)',
        'n_classes': 4,
        'loss': 'focal',
        'config_key': '4567',
        'conv_fn': 'vanilla_conv',
    }
    ,
    # UNet3D with WaveletViT 3D bottleneck (deterministic)
    'uwavevitnet': {
        'name': 'UNetWaveViT3D',
        'description': 'UNet3D with 3D Wavelet-ViT bottleneck (feature-domain, no VAE)',
        'n_classes': 4,
        'loss': 'focal',
        'config_key': '4567',
        'conv_fn': 'vanilla_conv',
    }
    ,
    
    # Preferred key for the same hybrid as above (UIIR + WaveViT bottleneck)
    'uiirwavevitnet': {
        'name': 'UIIRDFIIWaveViTNet3D',
        'description': 'UNet3D (IIR DF-II convs) with 3D Wavelet-ViT bottleneck (feature-domain, no VAE)',
        'n_classes': 4,
        'loss': 'focal',
        'config_key': '4567',
        'conv_fn': 'vanilla_conv',
    }
    ,
    # UNet3D variant using IIR3D layers
    'uiir': {
        'name': 'UIIRDFIINet3D',
        'description': 'UNet3D built with IIR3D layers in place of Conv3D',
        'n_classes': 4,
        'loss': 'focal',
        'config_key': '4567',
        'conv_fn': 'vanilla_conv',
        'bottleneck_fn': 'vanilla_bottleneck'
    }
    ,
    # Gφψ3D WaveViT variant with IIR3D conv replacements
    'giirwavevit': {
        'name': 'G3DIIRWaveViT',
        'description': 'G3D wavelet-native ViT with IIR3D conv replacements',
        'n_classes': 4,
        'loss': 'focal',
        'config_key': '4567',
        'conv_fn': 'vanilla_conv'
    }
}

# =============================================================================
# Model Factory Class
# =============================================================================

class ModelFactory:
    """
    Factory class for creating 3D segmentation models.

    This factory supports creating different model types with consistent
    interfaces and configurations. New model types can be easily added
    by extending the MODEL_CONFIGS dictionary and adding corresponding
    creation methods.
    """

    @staticmethod
    def create_model(
        model_type,
        input_size=64,
        *,
        n_classes=None,
        loss=None,
        class_weights=None,
        build=True,
        compile=True,
        optimizer=None,
        jit_compile=False,
        show_summary=False,
        wave=None,
    ):
        """
        Create and optionally build/compile the specified model.

        Args:
            model_type: Model type identifier ('G' for G3D, 'U' for UNet3D)
            input_size: Input dimension size (default 64 for patches, 256 for full-size)
            n_classes: Optional override for number of classes
            loss: Optional override for loss name passed to G3D wrapper
            class_weights: Optional class weights passed to G3D wrapper
            build: If True (default), call model.build with appropriate input shape
            compile: If True (default), compile with provided or default optimizer
            optimizer: Optional tf.keras optimizer; defaults to Adam(1e-4)
            jit_compile: Whether to enable XLA JIT at compile time (default False)
            show_summary: If True, print model.summary()
            wave: Wavelet name for G-type models (e.g., 'haar'); ignored for U-type models

        Returns:
            Keras model ready for training/inference

        Raises:
            ValueError: If model_type is not supported
        """
        if model_type not in MODEL_CONFIGS:
            supported_models = list(MODEL_CONFIGS.keys())
            raise ValueError(f"Unknown model type: {model_type}. Supported: {supported_models}")

        config = MODEL_CONFIGS[model_type]
        # Resolve overrides
        resolved_n_classes = n_classes or config['n_classes']
        resolved_loss = loss or config['loss']

        if model_type == 'G':
            model = ModelFactory._create_g3d_model(input_size, config, resolved_n_classes, resolved_loss, class_weights, wave)
        elif model_type == 'ufdstvitnet':
            model = ModelFactory._create_unetfdstvit_model(input_size, config, resolved_n_classes, resolved_loss, class_weights)
        elif model_type == 'U':
            model = ModelFactory._create_unet3d_model(input_size, config, resolved_n_classes, resolved_loss, class_weights)
        elif model_type == 'uvit':
            model = ModelFactory._create_unet3dvit_model(input_size, config, resolved_n_classes, resolved_loss, class_weights)
        elif model_type == 'gvit':
            model = ModelFactory._create_g3dvit_model(input_size, config, resolved_n_classes, resolved_loss, class_weights, wave)
        elif model_type == 'uattn':
            model = ModelFactory._create_unet3dattention_model(input_size, config, resolved_n_classes, resolved_loss, class_weights)
        elif model_type == 'gattn':
            model = ModelFactory._create_g3dattention_model(input_size, config, resolved_n_classes, resolved_loss, class_weights, wave)
        elif model_type == 'udwtattn':
            model = ModelFactory._create_unet3ddwtattn_model(input_size, config, resolved_n_classes, resolved_loss, class_weights)
        elif model_type == 'gwavevit':
            model = ModelFactory._create_g3dwavevit_model(input_size, config, resolved_n_classes, resolved_loss, class_weights, wave)
        elif model_type == 'shearmednet':
            model = ModelFactory._create_fdstunet3d_model(input_size, config, resolved_n_classes, resolved_loss, class_weights)
        elif model_type == 'shearmedfdstvitnet':
            model = ModelFactory._create_shearmedfdstvit_model(input_size, config, resolved_n_classes, resolved_loss, class_weights)
        elif model_type == 'cvshearmednet':
            model = ModelFactory._create_fdstcvaeunet3d_model(input_size, config, resolved_n_classes, resolved_loss, class_weights)
        elif model_type == 'cvshearmedwavevitnet':
            model = ModelFactory._create_cvshearmedwavevitnet_model(input_size, config, resolved_n_classes, resolved_loss, class_weights)
        # elif model_type == 'fdstcvaeunetfdstvitfdstcvaeunetfdstvit':
        #     model = ModelFactory._create_fdstcvaeunetfdstvit_model(input_size, config, resolved_n_classes, resolved_loss, class_weights)
        elif model_type == 'glifting':
            model = ModelFactory._create_g3dlifting_model(input_size, config, resolved_n_classes, resolved_loss, class_weights, wave)
        elif model_type == 'gminimal':
            model = ModelFactory._create_g3dminimal_model(input_size, config, resolved_n_classes, resolved_loss, class_weights, wave)
        elif model_type == 'cvunet':
            model = ModelFactory._create_cvunet_model(input_size, config, resolved_n_classes, resolved_loss, class_weights)
        elif model_type == 'cvuwavevitnet':
            model = ModelFactory._create_cvuwavevitnet_model(input_size, config, resolved_n_classes, resolved_loss, class_weights, wave)
        elif model_type == 'cvshearmedfdstvitnet':
            model = ModelFactory._create_cvshearmedfdstvitnet_model(input_size, config, resolved_n_classes, resolved_loss, class_weights)
        elif model_type == 'cvufdstvitnet':
            model = ModelFactory._create_cvufdstvitnet_model(input_size, config, resolved_n_classes, resolved_loss, class_weights)
        elif model_type == 'uwavevitnet':
            model = ModelFactory._create_unetwavevit_model(input_size, config, resolved_n_classes, resolved_loss, class_weights, wave)
        elif model_type == 'uiirwavevitnet':
            model = ModelFactory._create_unetwavevitediir_model(input_size, config, resolved_n_classes, resolved_loss, class_weights, wave)
        elif model_type == 'uiir':
            model = ModelFactory._create_unet3diir_model(input_size, config, resolved_n_classes, resolved_loss, class_weights)
        elif model_type == 'giirwavevit':
            model = ModelFactory._create_g3diirwavevit_model(input_size, config, resolved_n_classes, resolved_loss, class_weights, wave)
        else:
            # This should never happen due to the check above, but kept for safety
            raise ValueError(f"No creation method for model type: {model_type}")

        # Build/compile as requested
        if build:
            model.build(input_shape=(None, input_size, input_size, input_size, 1))
        if compile:
            # Uniform compile path: use provided optimizer or default Adam(1e-4)
            opt = optimizer or tf.keras.optimizers.Adam(1e-4)
            model.compile(optimizer=opt, jit_compile=jit_compile)
        if show_summary:
            try:
                model.summary()
            except Exception:
                pass
        return model

    @staticmethod
    def _create_g3d_model(input_size, config, n_classes, loss, class_weights, wave=None):
        """
        Create G3D model with specified configuration.

        Args:
            input_size: Input dimension size
            config: Model configuration dictionary

        Returns:
            Compiled G3D model
        """
        print(f"Creating {config['name']} model (input_size={input_size})...")

        G = Gφψ3D(
            input_shape=(input_size, input_size, input_size, 1),
            config=configs[config['config_key']],
            n_classes=n_classes,
            conv_fn=get_conv_fn(config['conv_fn']),
            pooling_fn=None,
            unpool_fn=None,
            bottleneck_fn=get_bottleneck_fn(config['bottleneck_fn']),
            output_kernel_regularizer=None,
            residual=False,
            Ψ=(wave or 'haar')
        )

        return ModelFactory._finalize_model(G, input_size, n_classes, loss, class_weights)

    @staticmethod
    def _create_unet3d_model(input_size, config, n_classes, loss, class_weights):
        """
        Create UNet3D model with specified configuration.

        Args:
            input_size: Input dimension size
            config: Model configuration dictionary

        Returns:
            Compiled UNet3D model
        """
        print(f"Creating {config['name']} model (input_size={input_size})...")

        if UNet3D is None:
            raise ValueError("UNet3D is not available in the current MEDNet package")

        unet_model = UNet3D(
            input_shape=(input_size, input_size, input_size, 1),
            config=configs[config['config_key']],
            n_classes=n_classes,
            conv_fn=get_conv_fn(config['conv_fn']),
            pooling_fn=None,
            unpool_fn=None,
            bottleneck_fn=get_bottleneck_fn(config['bottleneck_fn']),
            output_kernel_regularizer=None,
            one_hot_encode=True,
            residual=False
        )

        return ModelFactory._finalize_model(unet_model, input_size, n_classes, loss, class_weights)

    @staticmethod
    def _create_unetfdstvit_model(input_size, config, n_classes, loss, class_weights):
        print(f"Creating {config['name']} model (input_size={input_size})...")
        try:
            from MEDNet.UFDSTViTNet3D import UNetFDSTViT3D
        except Exception as _e:
            raise ImportError("UNetFDSTViT3D is not available in MEDNet")
        import os as _os
        def _get_int(name, default):
            try:
                return int(_os.environ.get(name, default))
            except Exception:
                return default
        J = _get_int('MEDNET_FDST_J_BOTT', _get_int('MEDNET_FDST_J', 2))
        L1 = _get_int('MEDNET_FDST_L1_BOTT', _get_int('MEDNET_FDST_L1', 4))
        embed_dim = _get_int('MEDNET_VIT_EMBED', 64)
        heads = _get_int('MEDNET_VIT_HEADS', 2)
        inner = UNetFDSTViT3D(
            input_shape=(input_size, input_size, input_size, 1),
            config=configs[config['config_key']],
            n_classes=n_classes,
            embed_dim=embed_dim,
            heads=heads,
            J=J,
            L1=L1,
            tokenizer="conv1d",
            token_conv_filters=None,
            gain_scale=1.0,
            use_feat_mixer=False,
            dropout=0.0,
            output_kernel_regularizer=None,
            one_hot_encode=True,
            residual=False,
        )
        try:
            inner.build((None, input_size, input_size, input_size, 1))
        except Exception:
            pass
        return ModelFactory._finalize_model(inner, input_size, n_classes, loss, class_weights)

    @staticmethod
    def _create_unetwavevit_model(input_size, config, n_classes, loss, class_weights, wave=None):
        """Create UNetWaveViT3D model (deterministic WaveletViT bottleneck) and wrap with common compile/loss handling."""
        print(f"Creating {config['name']} model (input_size={input_size})...")
        if UNetWaveViT3D is None:
            raise ImportError("UNetWaveViT3D is not available in MEDNet")

        import os as _os
        def _get_int(name, default):
            try:
                return int(_os.environ.get(name, default))
            except Exception:
                return default
        # Wavelet-ViT sizing knobs (keep minimal and safe)
        wvit_embed   = _get_int('MEDNET_WVIT_EMBED', 64)
        wvit_heads   = _get_int('MEDNET_WVIT_HEADS', 2)
        wvit_keydim  = _get_int('MEDNET_WVIT_KEYDIM', 16)
        wvit_levels  = _get_int('MEDNET_WVIT_LEVELS', 1)

        inner = UNetWaveViT3D(
            input_shape=(input_size, input_size, input_size, 1),
            config=configs[config['config_key']],
            n_classes=n_classes,
            embed_dim=wvit_embed,
            levels=wvit_levels,
            wave=(wave or 'haar'),
            heads=wvit_heads,
            key_dim=wvit_keydim,
            strength=0.25,
            level_decay=1.0,
            use_orient_mix=True,
            lp_global_if_small=True,
            max_tokens_global=8192,
            qkv_bias=True,
            dwt_compute_dtype='float32',
            prebuild_banks=True,
        )
        try:
            inner.build((None, input_size, input_size, input_size, 1))
        except Exception:
            pass
        return ModelFactory._finalize_model(inner, input_size, n_classes, loss, class_weights)

    @staticmethod
    def _create_unetwavevitediir_model(input_size, config, n_classes, loss, class_weights, wave=None):
        """Create UIIRDFIIWaveViTNet3D model (IIR conv blocks + deterministic WaveletViT bottleneck)."""
        print(f"Creating {config['name']} model (input_size={input_size})...")
        if UIIRDFIIWaveViTNet3D is None:
            raise ImportError("UIIRDFIIWaveViTNet3D is not available in MEDNet")

        import os as _os
        def _get_int(name, default):
            try:
                return int(_os.environ.get(name, default))
            except Exception:
                return default
        # Wavelet-ViT sizing knobs (mirror uwavevitnet defaults)
        wvit_embed   = _get_int('MEDNET_WVIT_EMBED', 64)
        wvit_heads   = _get_int('MEDNET_WVIT_HEADS', 2)
        wvit_keydim  = _get_int('MEDNET_WVIT_KEYDIM', 8)
        wvit_levels  = _get_int('MEDNET_WVIT_LEVELS', 1)

        inner = UIIRDFIIWaveViTNet3D(
            input_shape=(input_size, input_size, input_size, 1),
            config=configs[config['config_key']],
            n_classes=n_classes,
            embed_dim=wvit_embed,
            levels=wvit_levels,
            wave=(wave or 'haar'),
            heads=wvit_heads,
            key_dim=wvit_keydim,
            strength=0.25,
            level_decay=1.0,
            use_orient_mix=True,
            lp_global_if_small=True,
            max_tokens_global=2048,
            qkv_bias=True,
            dwt_compute_dtype='float32',
            prebuild_banks=True,
            iir_kwargs=None,
            output_kernel_regularizer=None,
            one_hot_encode=True,
            residual=False,
        )
        try:
            inner.build((None, input_size, input_size, input_size, 1))
        except Exception:
            pass
        return ModelFactory._finalize_model(inner, input_size, n_classes, loss, class_weights)

    @staticmethod
    def _create_unet3dattention_model(input_size, config, n_classes, loss, class_weights):
        """
        Create UNet3Dattention model with specified configuration.

        Returns:
            Compiled UNet3Dattention wrapped G3D model
        """
        print(f"Creating {config['name']} model (input_size={input_size})...")

        unet_attn = UNet3Dattention(
            input_shape=(input_size, input_size, input_size, 1),
            config=configs[config['config_key']],
            n_classes=n_classes,
            conv_fn=get_conv_fn(config['conv_fn']),
            pooling_fn=None,
            unpool_fn=None,
            bottleneck_fn=get_bottleneck_fn(config.get('bottleneck_fn', 'vanilla_bottleneck')),
            output_kernel_regularizer=None,
            one_hot_encode=True,
            residual=False
        )

        return ModelFactory._finalize_model(unet_attn, input_size, n_classes, loss, class_weights)

    @staticmethod
    def _create_unet3dvit_model(input_size, config, n_classes, loss, class_weights):
        """
        Create UNet3DViT model with specified configuration.

        Args:
            input_size: Input dimension size
            config: Model configuration dictionary

        Returns:
            Compiled UNet3DViT wrapped G3D model
        """
        print(f"Creating {config['name']} model (input_size={input_size})...")

        if UNet3DViT is None:
            raise ValueError("UNet3DViT is not available in the current MEDNet package")

        uvit = UNet3DViT(
            input_shape=(input_size, input_size, input_size, 1),
            config=configs[config['config_key']],
            n_classes=n_classes,
            conv_fn=get_conv_fn(config['conv_fn']),
            pooling_fn=None,
            unpool_fn=None,
            output_kernel_regularizer=None,
            one_hot_encode=True,
            residual=False
        )

        return ModelFactory._finalize_model(uvit, input_size, n_classes, loss, class_weights)

    @staticmethod
    def _create_g3dvit_model(input_size, config, n_classes, loss, class_weights, wave=None):
        """
        Create G3DViT model with specified configuration.

        Returns:
            Compiled G3DViT wrapped G3D model
        """
        print(f"Creating {config['name']} model (input_size={input_size})...")

        if Gφψ3D_ViT is None:
            raise ValueError("G3DViT is not available in the current MEDNet package")

        gvit = Gφψ3D_ViT(
            input_shape=(input_size, input_size, input_size, 1),
            config=configs[config['config_key']],
            n_classes=n_classes,
            conv_fn=get_conv_fn(config['conv_fn']),
            pooling_fn=None,
            unpool_fn=None,
            output_kernel_regularizer=None,
            one_hot_encode=True,
            residual=False,
            Ψ=(wave or 'haar')
        )

        return ModelFactory._finalize_model(gvit, input_size, n_classes, loss, class_weights)

    @staticmethod
    def _create_g3dattention_model(input_size, config, n_classes, loss, class_weights, wave=None):
        """
        Create G3Dattention model with specified configuration.

        Returns:
            Compiled G3Dattention wrapped G3D model
        """
        print(f"Creating {config['name']} model (input_size={input_size})...")

        gattn = G3Dattention(
            input_shape=(input_size, input_size, input_size, 1),
            config=configs[config['config_key']],
            n_classes=n_classes,
            conv_fn=get_conv_fn(config['conv_fn']),
            pooling_fn=None,
            unpool_fn=None,
            bottleneck_fn=get_bottleneck_fn(config.get('bottleneck_fn', 'vanilla_bottleneck')),
            output_kernel_regularizer=None,
            one_hot_encode=True,
            residual=False,
            Ψ=(wave or 'haar')
        )

        return ModelFactory._finalize_model(gattn, input_size, n_classes, loss, class_weights)

    @staticmethod
    def _create_g3dwavevit_model(input_size, config, n_classes, loss, class_weights, wave=None):
        """
        Create G3DwaveViT model with specified configuration.

        Returns:
            Compiled G3DwaveViT wrapped G3D model
        """
        print(f"Creating {config['name']} model (input_size={input_size})...")

        if Gφψ3D_waveViT is None:
            raise ValueError("G3DwaveViT is not available in the current MEDNet package")

        gwavevit = Gφψ3D_waveViT(
            input_shape=(input_size, input_size, input_size, 1),
            config=configs[config['config_key']],
            n_classes=n_classes,
            conv_fn=get_conv_fn(config['conv_fn']),
            pooling_fn=None,
            unpool_fn=None,
            output_kernel_regularizer=None,
            one_hot_encode=True,
            residual=False,
            Ψ=(wave or 'haar')
        )

        return ModelFactory._finalize_model(gwavevit, input_size, n_classes, loss, class_weights)

    @staticmethod
    def _create_fdstunet3d_model(input_size, config, n_classes, loss, class_weights):
        """
        Create FDSTUNet3D model with specified configuration.

        Returns:
            Compiled FDSTUNet3D model
        """
        print(f"Creating {config['name']} model (input_size={input_size})...")

        if FDSTUNet3D is None:
            raise ValueError("FDSTUNet3D is not available in the current MEDNet package")

        fdst_model = FDSTUNet3D(
            input_shape=(input_size, input_size, input_size, 1),
            n_classes=n_classes,
            J=2,
            L1=4,
            base_filters=16,
            cone_mode='soft',
            rotation_mode='union',
            target_redundancy=2.0,
            feature_dropout=0.0,
            normalize_per_channel=False,
            final_activation=None,
            complex_repr='magnitude'
        )

        return ModelFactory._finalize_model(fdst_model, input_size, n_classes, loss, class_weights)

    @staticmethod
    def _create_shearmedfdstvit_model(input_size, config, n_classes, loss, class_weights):
        """Create ShearMEDFDSTViTNet3D model and wrap with common compile/loss handling."""
        print(f"Creating {config['name']} model (input_size={input_size})...")
        if ShearMEDFDSTViTNet3D is None:
            raise ImportError("ShearMEDFDSTViTNet3D is not available in MEDNet")

        import os as _os
        # Encoder FDST pyramid
        _J = int(_os.environ.get('MEDNET_FDST_J', '2'))
        _L1 = int(_os.environ.get('MEDNET_FDST_L1', '4'))
        # Bottleneck FDST pyramid (env-overridable; None lets factory fallback)
        def _maybe_int(name):
            v = _os.environ.get(name)
            try:
                return int(v) if v is not None else None
            except Exception:
                return None
        _Jb = _maybe_int('MEDNET_FDST_J_BOTT')
        _L1b = _maybe_int('MEDNET_FDST_L1_BOTT')
        # ViT sizing knobs
        def _get_int(name, default):
            try:
                return int(_os.environ.get(name, default))
            except Exception:
                return default
        _vit_embed = _get_int('MEDNET_VIT_EMBED', 64)
        _vit_heads = _get_int('MEDNET_VIT_HEADS', 2)

        inner = ShearMEDFDSTViTNet3D(
            input_shape=(input_size, input_size, input_size, 1),
            n_classes=n_classes,
            J=_J,
            L1=_L1,
            base_filters=16,
            cone_mode='soft',
            rotation_mode='union',
            target_redundancy=2.0,
            normalize_per_channel=False,
            complex_repr='magnitude',
            embed_dim=_vit_embed,
            heads=_vit_heads,
            J_bott=_Jb,
            L1_bott=_L1b,
            tokenizer='conv1d',
            token_conv_filters=None,
            gain_scale=1.0,
            use_feat_mixer=False,
            dropout=0.0,
            final_activation=None,
        )
        try:
            inner.build((None, input_size, input_size, input_size, 1))
        except Exception:
            pass
        return ModelFactory._finalize_model(inner, input_size, n_classes, loss, class_weights)

    @staticmethod
    def _create_fdstcvaeunet3d_model(input_size, config, n_classes, loss, class_weights):
        """Create FDSTCVAEUNet3D model with CVAE bottleneck and wrap with G3D."""
        print(f"Creating {config['name']} model (input_size={input_size})...")
        if FDSTCVAEUNet3D is None:
            raise ValueError("FDSTCVAEUNet3D is not available in the current MEDNet package")
        inner = FDSTCVAEUNet3D(
            input_shape=(input_size, input_size, input_size, 1),
            n_classes=n_classes,
            J=2,
            L1=4,
            base_filters=16,
            cone_mode='soft',
            rotation_mode='union',
            target_redundancy=2.0,
            feature_dropout=0.0,
            normalize_per_channel=False,
            final_activation=None,
            complex_repr='magnitude',
            latent_dim=128,
            fuse_skip=True,
        )
        return ModelFactory._finalize_model(inner, input_size, n_classes, loss, class_weights)

    @staticmethod
    def _create_cvufdstvitnet_model(input_size, config, n_classes, loss, class_weights):
        """Create CVUFDSTViTNet3D model and wrap with common compile/loss handling."""
        print(f"Creating {config['name']} model (input_size={input_size})...")
        if CVUFDSTViTNet3D is None:
            raise ImportError("CVUFDSTViTNet3D is not available in MEDNet")

        # Defaults: bottleneck J=1, L1=4, ViT embed 128, heads 4; allow env override
        import os as _os
        _Jb = int(_os.environ.get('MEDNET_FDST_J_BOTT', '1'))
        _L1b = int(_os.environ.get('MEDNET_FDST_L1_BOTT', '4'))
        # ViT sizing knobs
        def _get_int(name, default):
            try:
                return int(_os.environ.get(name, default))
            except Exception:
                return default
        _vit_embed = _get_int('MEDNET_VIT_EMBED', 128)
        _vit_heads = _get_int('MEDNET_VIT_HEADS', 4)
        # KL weight override
        def _get_float(name, default):
            try:
                return float(_os.environ.get(name, default))
            except Exception:
                return default
        _kl_scale = _get_float('MEDNET_VIT_KL_WEIGHT', 1e-4)

        inner = CVUFDSTViTNet3D(
            input_shape=(input_size, input_size, input_size, 1),
            n_classes=n_classes,
            J_bott=_Jb,
            L1_bott=_L1b,
            vit_embed_dim=_vit_embed,
            vit_heads=_vit_heads,
            kl_scale=_kl_scale,
            # Use model defaults for optional features to keep factory clean
        )
        try:
            inner.build((None, input_size, input_size, input_size, 1))
        except Exception:
            pass
        return ModelFactory._finalize_model(inner, input_size, n_classes, loss, class_weights)

    @staticmethod
    def _create_cvshearmedfdstvitnet_model(input_size, config, n_classes, loss, class_weights):
        """Create CVShearMEDFDSTViTNet3D model and wrap with compile/loss handling."""
        print(f"Creating {config['name']} model (input_size={input_size})...")
        if FDSTCVAEUNetFDSTViT3D is None:
            raise ImportError("CVShearMEDFDSTViTNet3D is not available in MEDNet")

        import os as _os
        # Representation pyramid (skips)
        _J = int(_os.environ.get('MEDNET_FDST_J', '2'))
        _L1 = int(_os.environ.get('MEDNET_FDST_L1', '4'))
        # Bottleneck FDST settings
        _Jb = int(_os.environ.get('MEDNET_FDST_J_BOTT', '1'))
        _L1b = int(_os.environ.get('MEDNET_FDST_L1_BOTT', '4'))
        # ViT sizing knobs
        def _get_int(name, default):
            try:
                return int(_os.environ.get(name, default))
            except Exception:
                return default
        _vit_embed = _get_int('MEDNET_VIT_EMBED', 64)
        _vit_heads = _get_int('MEDNET_VIT_HEADS', 2)

        inner = FDSTCVAEUNetFDSTViT3D(
            in_shape=(input_size, input_size, input_size, 1),
            num_classes=n_classes,
            J=_J,
            L1=_L1,
            J_bott=_Jb,
            L1_bott=_L1b,
            embed_dim=_vit_embed,
            heads=_vit_heads,
            latent_channels=None,
            kl_weight=1e-4,
            use_feat_mixer=False,
            gain_scale=1.0,
            injection='residual',
            vae_mode='token',
            base_filters=16,
            feature_dropout=0.0,
            name=config['name'],
        )
        try:
            inner.build((None, input_size, input_size, input_size, 1))
        except Exception:
            pass
        return ModelFactory._finalize_model(inner, input_size, n_classes, loss, class_weights)

    @staticmethod
    def _create_cvshearmedwavevitnet_model(input_size, config, n_classes, loss, class_weights):
        """Create CVShearMEDWaveViTNet3D model and wrap with G3D-like compile/loss handling."""
        print(f"Creating {config['name']} model (input_size={input_size})...")
        if CVShearMEDWaveViTNet3D is None:
            raise ImportError("CVShearMEDWaveViTNet3D is not available.")
        inner = CVShearMEDWaveViTNet3D(
            input_shape=(input_size, input_size, input_size, 1),
            n_classes=n_classes,
            J=2,
            L1=4,
            base_filters=16,
            cone_mode='soft',
            rotation_mode='union',
            target_redundancy=2.0,
            feature_dropout=0.0,
            normalize_per_channel=False,
            final_activation=None,
            complex_repr='magnitude',
            Ψ='haar',
            wvit_levels=1,
            vit_embed_dim=128,
            vit_heads=4,
            vit_depth=2,
            vit_key_dim=16,
            kl_scale=1.0,
        )
        return ModelFactory._finalize_model(inner, input_size, n_classes, loss, class_weights)

    @staticmethod
    # def _create_fdstcvaeunetfdstvit_model(input_size, config, n_classes, loss, class_weights):
    #     """Removed: consolidated onto cvufdstvitnet (coefficient-domain FDSTViT) only."""
    #     raise NotImplementedError

    @staticmethod
    def _create_g3dlifting_model(input_size, config, n_classes, loss, class_weights, wave=None):
        """
        Create G3DLifting model with specified configuration.

        Returns:
            Compiled G3DLifting wrapped G3D model
        """
        print(f"Creating {config['name']} model (input_size={input_size})...")

        if Gφψ3D_Lifting is None:
            raise ValueError("G3DLifting is not available in the current MEDNet package")

        glifting = Gφψ3D_Lifting(
            input_shape=(input_size, input_size, input_size, 1),
            config=configs[config['config_key']],
            n_classes=n_classes,
            conv_fn=get_conv_fn(config['conv_fn']),
            pooling_fn=None,
            unpool_fn=None,
            bottleneck_fn=get_bottleneck_fn(config['bottleneck_fn']),
            output_kernel_regularizer=None,
            one_hot_encode=True,
            residual=False,
            wavelet_refine=True,
            Ψ=(wave or 'haar')
        )

        return ModelFactory._finalize_model(glifting, input_size, n_classes, loss, class_weights)

    @staticmethod
    def _create_g3dminimal_model(input_size, config, n_classes, loss, class_weights, wave=None):
        """
        Create G3D_minimal model with specified configuration.

        Returns:
            Compiled minimal G3D wrapped model
        """
        print(f"Creating {config['name']} model (input_size={input_size})...")

        if Gφψ3D_Minimal is None:
            raise ValueError("G3D_minimal is not available in the current MEDNet package")

        inner = Gφψ3D_Minimal(
            Ψ=(wave or 'haar'),
            n_classes=n_classes,
            n_input_channels=1,
            input_shape=(input_size, input_size, input_size, 1),
            config=configs[config['config_key']],
            compile=False,
        )

        return ModelFactory._finalize_model(inner, input_size, n_classes, loss, class_weights)

    @staticmethod
    

    @staticmethod
    def _create_cvunet_model(input_size, config, n_classes, loss, class_weights):
        print(f"Creating {config['name']} model (input_size={input_size})...")
        if CVAEUNet3D is None:
            raise ValueError("CVAEUNet3D is not available in the current MEDNet package")
        inner = CVAEUNet3D(
            input_shape=(input_size, input_size, input_size, 1),
            n_classes=n_classes,
            config=configs[config['config_key']],
            latent_dim=512,
            compression_ratio=None,
            conv_fn=None,           # use CVAE defaults to avoid API mismatch
            pooling_fn=None,        # use internal default pooling
            upsampling_fn=None,     # use internal default upsampling
        )
        return inner

    @staticmethod
    def _create_cvuwavevitnet_model(input_size, config, n_classes, loss, class_weights, wave=None):
        print(f"Creating {config['name']} model (input_size={input_size})...")
        if CVUWaveViTNet3D is None:
            raise ValueError("CVUWaveViTNet3D is not available in the current MEDNet package")
        # size knobs via env
        import os
        def _get_int(name, default):
            try:
                return int(os.environ.get(name, default))
            except Exception:
                return default
        vit_embed_dim = _get_int('MEDNET_WVIT_EMBED', 128)
        vit_depth     = _get_int('MEDNET_WVIT_DEPTH', 2)
        vit_heads     = _get_int('MEDNET_WVIT_HEADS', 4)
        vit_key_dim   = _get_int('MEDNET_WVIT_KEYDIM', 16)
        wvit_levels   = _get_int('MEDNET_WVIT_LEVELS', 1)

        inner = CVUWaveViTNet3D(
            input_shape=(input_size, input_size, input_size, 1),
            config=configs[config['config_key']],
            n_classes=n_classes,
            Ψ=(wave or 'haar'),
            wvit_levels=wvit_levels,
            vit_embed_dim=vit_embed_dim,
            vit_heads=vit_heads,
            vit_depth=vit_depth,
            vit_key_dim=vit_key_dim,
        )
        # Wrap in G3D to unify compile, metrics (IoU/Dice), and logging with other models.
        # Inner model contributes KL via add_loss; G3D provides focal (or selected) loss and metrics.
        return ModelFactory._finalize_model(inner, input_size, n_classes, loss, class_weights)

    @staticmethod
    def _create_unet3ddwtattn_model(input_size, config, n_classes, loss, class_weights):
        """
        Create UNet3Ddwtattn model with specified configuration.

        Returns:
            Compiled UNet3Ddwtattn wrapped G3D model
        """
        print(f"Creating {config['name']} model (input_size={input_size})...")

        unet_dwt_attn = UNet3Ddwtattn(
            input_shape=(input_size, input_size, input_size, 1),
            config=configs[config['config_key']],
            n_classes=n_classes,
            conv_fn=get_conv_fn(config['conv_fn']),
            pooling_fn=None,
            unpool_fn=None,
            bottleneck_fn=get_bottleneck_fn(config.get('bottleneck_fn', 'vanilla_bottleneck')),
            output_kernel_regularizer=None,
            one_hot_encode=True,
            residual=False,
            Ψ='haar'
        )

        return ModelFactory._finalize_model(unet_dwt_attn, input_size, n_classes, loss, class_weights)

    @staticmethod
    def _create_unet3diir_model(input_size, config, n_classes, loss, class_weights):
        """Create UNet3DIIR model and wrap with G3D for loss/class weights."""
        print(f"Creating {config['name']} model (input_size={input_size})...")
        if UIIRNet3D is None:
            raise ValueError("UNet3DIIR is not available in the current MEDNet package")
        # Optional channel override via env, e.g., MEDNET_CHANNELS="8,16,32,64"
        conf_tuple = configs[config['config_key']]
        ch_override = os.environ.get('MEDNET_CHANNELS')
        if ch_override:
            try:
                parsed = tuple(int(x.strip()) for x in ch_override.split(','))
                if len(parsed) == 4:
                    conf_tuple = parsed
                    print(f"[model_factory] Using MEDNET_CHANNELS override: {conf_tuple}")
            except Exception:
                pass

        inner = UIIRNet3D(
            input_shape=(input_size, input_size, input_size, 1),
            config=conf_tuple,
            n_classes=n_classes,
            one_hot_encode=True,
            residual=False,
        )
        return ModelFactory._finalize_model(inner, input_size, n_classes, loss, class_weights)

    @staticmethod
    def _create_g3diirwavevit_model(input_size, config, n_classes, loss, class_weights, wave=None):
        """Create G3DIIRWaveViT model variant and wrap with G3D for training."""
        print(f"Creating {config['name']} model (input_size={input_size})...")
        if Gφψ3D_iirWaveViT is None:
            raise ValueError("G3DIIRWaveViT is not available in the current MEDNet package")
        # Env-driven light knobs to mitigate OOM without changing CLI
        # Channel widths override: e.g., MEDNET_CHANNELS="8,16,32,64"
        conf_tuple = configs[config['config_key']]
        ch_override = os.environ.get('MEDNET_CHANNELS')
        if ch_override:
            try:
                parsed = tuple(int(x.strip()) for x in ch_override.split(','))
                if len(parsed) == 4:
                    conf_tuple = parsed
                    print(f"[model_factory] Using MEDNET_CHANNELS override: {conf_tuple}")
            except Exception:
                pass

        # Wavelet-ViT size knobs
        def _get_int(name, default):
            try:
                return int(os.environ.get(name, default))
            except Exception:
                return default
        vit_embed_dim = _get_int('MEDNET_WVIT_EMBED', 128)
        vit_depth     = _get_int('MEDNET_WVIT_DEPTH', 2)
        vit_heads     = _get_int('MEDNET_WVIT_HEADS', 4)
        vit_key_dim   = _get_int('MEDNET_WVIT_KEYDIM', 16)
        wvit_levels   = _get_int('MEDNET_WVIT_LEVELS', 1)
        wvit_tokens   = _get_int('MEDNET_WVIT_TOKENS', 8192)

        inner = Gφψ3D_iirWaveViT(
            input_shape=(input_size, input_size, input_size, 1),
            config=conf_tuple,
            n_classes=n_classes,
            Ψ=(wave or 'haar'),
            one_hot_encode=True,
            residual=False,
            vit_embed_dim=vit_embed_dim,
            vit_depth=vit_depth,
            vit_heads=vit_heads,
            vit_key_dim=vit_key_dim,
            wvit_levels=wvit_levels,
            wvit_max_tokens_global=wvit_tokens,
        )
        return ModelFactory._finalize_model(inner, input_size, n_classes, loss, class_weights)

    @staticmethod
    def _finalize_model(inner_model, input_size, n_classes, loss, class_weights):
        """
        Finalize model by creating G3D wrapper, building, compiling, and summarizing.

        Args:
            inner_model: The inner model (Gφψ3D or UNet3D)
            input_size: Input dimension size for building
            config: Model configuration dictionary

        Returns:
            Finalized model
        """
        model = G3D(
            input_shape=(input_size, input_size, input_size, 1),
            model=inner_model,
            loss=loss,
            n_classes=n_classes,
            class_weights=class_weights,
        )
        return model

    @staticmethod
    def get_model_info(model_type):
        """
        Get information about a specific model type.

        Args:
            model_type: Model type identifier

        Returns:
            Dictionary with model information

        Raises:
            ValueError: If model_type is not supported
        """
        if model_type not in MODEL_CONFIGS:
            supported_models = list(MODEL_CONFIGS.keys())
            raise ValueError(f"Unknown model type: {model_type}. Supported: {supported_models}")

        return MODEL_CONFIGS[model_type].copy()

    @staticmethod
    def get_supported_models():
        """
        Get list of supported model types.

        Returns:
            List of supported model type identifiers
        """
        return list(MODEL_CONFIGS.keys())

def create_model(model_type, input_size=64, **kwargs):
    """
    Convenience function to create a model using the factory.

    This function provides backward compatibility and a simpler interface
    for creating models.

    Args:
        model_type: Model type identifier ('G' for G3D, 'U' for UNet3D)
        input_size: Input dimension size

    Returns:
        Keras model
    """
    return ModelFactory.create_model(model_type, input_size, **kwargs)

def get_supported_models():
    """
    Convenience function to get supported model types.

    Returns:
        List of supported model type identifiers
    """
    return ModelFactory.get_supported_models()

def get_model_info(model_type):
    """
    Convenience function to get model information.

    Args:
        model_type: Model type identifier

    Returns:
        Dictionary with model information
    """
    return ModelFactory.get_model_info(model_type)
