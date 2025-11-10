import tensorflow as tf
import keras


@tf.keras.utils.register_keras_serializable()
class ZScoreNormalize(tf.keras.layers.Layer):
    """Z-score normalize along spatial axes for N-dimensional data, optionally followed by min-max scaling
    
    Example input shape is (batch, n, ..., n, channels)
    Normalization happens along axes [n,...n], i.e. all the spatial axes
    with batch and channel axis excluded. Optionally, min-max scaling is applied after Z-score normalization.
    
    Args:
        epsilon: Small float added to denominators for numerical stability.
        min_max_scale: If True, apply min-max scaling after Z-score normalization.

      
        tf-nd-utils: Multidimensional utility layers in TensorFlow.
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
    --kkt@7Jun25
    """
    def __init__(self, epsilon=1e-8, min_max_scale=True, **kwargs):
        super().__init__(**kwargs)
        self.epsilon = epsilon
        self.min_max_scale = min_max_scale

    def call(self, inputs):
        # Determine spatial axes dynamically (works for 4D or 5D)
        spatial_axes = list(range(1, len(inputs.shape) - 1))  # Exclude batch and channel dims
        
        # Z-score normalization
        mean = tf.reduce_mean(inputs, axis=spatial_axes, keepdims=True)
        std = tf.math.reduce_std(inputs, axis=spatial_axes, keepdims=True)
        normalized = (inputs - mean) / (std + self.epsilon)
        
        if self.min_max_scale:
            # Min-max scaling to [0, 1]
            min_val = tf.reduce_min(normalized, axis=spatial_axes, keepdims=True)
            max_val = tf.reduce_max(normalized, axis=spatial_axes, keepdims=True)
            normalized = (normalized - min_val) / (max_val - min_val + self.epsilon)
        
        return normalized

    def get_config(self):
        config = super().get_config()
        config.update({
            "epsilon": self.epsilon,
            "min_max_scale": self.min_max_scale,
        })
        return config