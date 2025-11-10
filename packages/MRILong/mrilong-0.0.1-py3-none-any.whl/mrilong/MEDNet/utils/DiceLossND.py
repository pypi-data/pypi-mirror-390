import tensorflow as tf

@tf.keras.utils.register_keras_serializable()
class DiceLoss(tf.keras.losses.Loss):
    """ Multi-class weighted Dice loss using Keras' built-in Dice loss (`reduction='none'`).
        Applies the Dice loss independently to each class and combines them with class weights.
    
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
    """
    def __init__(self, class_weights=None, name="weighted_multiclass_dice"):
        super().__init__(name=name, reduction=tf.keras.losses.Reduction.SUM)

        self.class_weights_list = class_weights
        self.class_weights = tf.constant(class_weights, dtype=tf.float32) if class_weights is not None else None
        self.dice_fn = tf.keras.losses.Dice(reduction='none')  # ✅ Your objective

    def call(self, y_true, y_pred):
        """
        Args:
            y_true: Tensor of shape (B, ..., C), one-hot ground truth.
            y_pred: Tensor of shape (B, ..., C), softmax probabilities.
        Returns:
            Scalar loss value.
        """
        # Input validation
        if y_true.shape[-1] != y_pred.shape[-1]:
            raise ValueError("Mismatch in number of classes between y_true and y_pred")

        num_classes = y_pred.shape[-1]
        if num_classes is None:
            raise ValueError("Number of classes must be statically defined in y_pred.shape[-1]")

        per_class_losses = []

        for i in range(num_classes):
            y_true_c = y_true[..., i]
            y_pred_c = y_pred[..., i]

            # Get per-batch dice loss for class i
            loss_c = self.dice_fn(y_true_c, y_pred_c)  # shape: (batch,)

            if self.class_weights is not None:
                loss_c *= self.class_weights[i]  # apply weight for this class

            per_class_losses.append(loss_c)  # shape: (batch,)

        # Stack to shape: (batch, num_classes)
        losses = tf.stack(per_class_losses, axis=-1)

        # Return mean loss across batch and class dimensions
        return tf.reduce_mean(losses)

    def get_config(self):
        return {
            **super().get_config(),
            "class_weights": self.class_weights_list,
        }
