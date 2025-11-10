import tensorflow as tf
from tensorflow.keras.layers import Input, Conv3D, Conv3DTranspose, MaxPool3D, Dropout, BatchNormalization, Activation, Concatenate
from tensorflow.keras import regularizers
from MEDNet.utils.ZscoreNormalizeND import ZScoreNormalize

from MEDNet.G3D import default_conv, default_pooling, default_bottleneck
#, default_upsample

def default_upsample(filters, x, activation='relu'):
    return Conv3DTranspose(filters, (2, 2, 2), strides=(2, 2, 2), padding='same')(x)


# def conv3D_block(x, filters, activation='relu'):
#     x = Conv3D(filters, 3, padding='same')(x)
#     x = Dropout(0.1)(x)
#     x = Conv3D(filters, 3, padding='same')(x)
#     x = BatchNormalization()(x)
#     return Activation(activation)(x)

def UNet3D(
    input_shape=(32, 32, 32, 1),
    config=(16, 32, 64, 128),
    n_classes=4,
    conv_fn=None,               ## scope for other convolutional systems
    pooling_fn=None,            ## scope for other downsampling systems
    unpool_fn=None,             ## scope for other upsampling systems
    bottleneck_fn=None,         ## scope for other bottleneck systems
    output_kernel_regularizer=None,
    one_hot_encode=True,
    residual=False):
    """ A concise Unet3D functional model (baseline)

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
    # a, b, c, d  = config
    # Policy: None => no regularizer; otherwise use default L1L2
    if output_kernel_regularizer is not None:
        output_kernel_regularizer = regularizers.L1L2(l1=1e-6, l2=1e-5)
    """system configs"""

    inputs = Input(shape=input_shape)
    x = ZScoreNormalize()(inputs)
    
    skips = []
    for filters in config:
        # x = conv3D_block(x, filters)
        x = conv(filters, x)
        skips.append(x)
        x = pool(x)
        # x = MaxPool3D(pool_size=2)(x)
    
    # x = conv3D_block(x, filters=config[-1]*2)
    x = bottleneck(x)

    for i, filters in reversed(list(enumerate(config))):
        # x = Conv3DTranspose(filters, 2, strides=2, padding='same')(x)
        x = up(filters, x)
        x = Concatenate()([x, skips[i]])
        x = conv(filters, x)
        # x = conv3D_block(x, filters)

    if residual:
        x = Concatenate()([x, inputs])

    if one_hot_encode==True: 
        last_activation = 'softmax'
    else: last_activation=None    
    outputs = Conv3D(
        n_classes, 
        (1, 1, 1),
        # kernel_regularizer=regularizers.L2(1e-4),
        kernel_regularizer=output_kernel_regularizer,
        # bias_regularizer=regularizers.L2(1e-4),
        # activity_regularizer=regularizers.L2(1e-5), 
        activation=last_activation,
        # activation="sigmoid"
        )(x)
    
    # outputs = Conv3D(n_classes, 1, activation='softmax')(x)
    return tf.keras.Model(inputs, outputs, name='Unet3D')

if __name__=='__main__':
    # Unet3D(input_shape=(32,32,32,1), residual=True).summary()

    n = 32
    input_shape = (n,n,n,1)
    config=(16, 32, 64, 128) 
    n_classes=4
    # conv_fn=None,               ## scope for other convolutional systems
    # pooling_fn=None,            ## scope for other downsampling systems
    # unpool_fn=None,
    residual=False,
    U = UNet3D(
        input_shape=input_shape, 
        config=config, 
        n_classes=n_classes, 
        residual=residual)
    # G = Gφψ3D(
    #     input_shape=input_shape, 
    #     config=config, 
    #     n_classes=n_classes, 
    #     conv_fn=None,               ## scope for other convolutional systems
    #     pooling_fn=None,            ## scope for other downsampling systems
    #     unpool_fn=None,
    #     residual=residual,
    #     Ψ='haar'
    #     )
    
    from MEDNet.G3Dv1 import G3D
    # model = G3D(input_shape=(n,n,n,1), loss='focal', class_weights=[0.1, 0.2, 0.3, 0.5], residual=True)
    model = G3D(input_shape=(n,n,n,1), model=U,  loss='dice', class_weights=[0.1, 0.2, 0.3, 0.5])
    # model.build(input_shape=(None, n, n, n, 1))
    model.compile(optimizer=tf.keras.optimizers.Adam(1e-4))
    model.summary()

    ## Sample train
    X_train = tf.random.normal((2, n, n, n, 1))
    Y_train = tf.random.uniform((2, n, n, n, 4))
    
    train_dataset = tf.data.Dataset.from_tensor_slices((X_train, Y_train)).batch(2)

    model.fit(train_dataset, epochs=5)