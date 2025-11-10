import tensorflow as tf 
from keras import regularizers

def default_bottleneck(
    input_tensor, scale=2, 
    use_leaky_relu=False, norm='batch', 
    use_dropout=True, dropout_rate=0.2, 
    kernel_regularizer=regularizers.L1L2(l1=1e-6, l2=1e-5)):
    # Get static number of input channels
    in_channels = input_tensor.shape[-1]
    assert in_channels is not None, "Input channel dimension must be defined"

    filters = in_channels * scale

    x = tf.keras.layers.Conv3D(
        filters, kernel_size=3, padding='same',
        kernel_regularizer=kernel_regularizer,
        name='latent_conv_1')(input_tensor)
    if norm == 'batch':
        x = tf.keras.layers.BatchNormalization()(x)
    x = tf.keras.layers.LeakyReLU(alpha=0.01)(x) if use_leaky_relu else tf.keras.layers.ReLU()(x)

    x = tf.keras.layers.Conv3D(
        filters, kernel_size=3, padding='same',
        kernel_regularizer=kernel_regularizer,
        name='latent_conv_2')(x)
    if norm == 'batch':
        x = tf.keras.layers.BatchNormalization()(x)
    x = tf.keras.layers.LeakyReLU(alpha=0.01)(x) if use_leaky_relu else tf.keras.layers.ReLU()(x)

    if use_dropout:
        x = tf.keras.layers.SpatialDropout3D(rate=dropout_rate)(x)

    return x