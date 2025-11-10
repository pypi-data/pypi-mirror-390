from tensorflow.keras import layers, regularizers
from tensorflow.keras.layers import GroupNormalization

def default_conv_block(
    filters, input_tensor, 
    use_leaky_relu=True, 
    # norm='batch',
    norm='group', groups=8,
    use_dropout=False, dropout_rate=0.2,
    kernel_regularizer=regularizers.L1L2(l1=1e-6, l2=1e-5),
    # name_prefix='conv_block'
    ):

    def get_norm():
        if norm == 'batch':
            return layers.BatchNormalization()
        elif norm == 'group':
            return GroupNormalization(groups=groups, axis=-1)
        else:
            raise ValueError(f"Unsupported norm type: {norm}")

    # Activation choice
    Activation = layers.LeakyReLU(alpha=0.01) if use_leaky_relu else layers.ReLU()

    # First conv layer
    x = layers.Conv3D(filters, kernel_size=3, padding='same',
                      kernel_regularizer=kernel_regularizer)(input_tensor)
    x = get_norm()(x)
    x = Activation(x)

    # Second conv layer
    x = layers.Conv3D(filters, kernel_size=3, padding='same',
                      kernel_regularizer=kernel_regularizer)(x)
    x = get_norm()(x)
    x = Activation(x)

    # Optional dropout
    if use_dropout:
        x = layers.SpatialDropout3D(rate=dropout_rate)(x)

    return x