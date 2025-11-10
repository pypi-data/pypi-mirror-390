import tensorflow as tf

@tf.keras.utils.register_keras_serializable()
class Dice(tf.keras.metrics.Metric):
    """ Computes the Dice score for a single class ID using tf.keras.losses.Dice(reduction='none').
        Instantiate separately for each class to get per-class Dice.
    
        Should work similar to IoU metric of tf by using a target_class_id   

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
    
    ---kkt@19Jun2025"""
    def __init__(self, target_class_ids, name=None, **kwargs):
        if not isinstance(target_class_ids, (list, tuple)) or len(target_class_ids) != 1:
            raise ValueError("For per-class Dice, target_class_ids must be a list with exactly one class index.")

        self.class_id = target_class_ids[0]
        name = name or f"dice_class_{self.class_id}"

        super().__init__(name=name, **kwargs)
        self.loss_fn = tf.keras.losses.Dice(reduction='none')
        self.dice_sum = self.add_weight(name="dice_sum", initializer="zeros")
        self.count = self.add_weight(name="count", initializer="zeros")

    def update_state(self, y_true, y_pred, sample_weight=None):
        ## new patch for sparse case
        # y_pred: [batch, ..., n_classes]
        # y_true: [batch, ...] (sparse) or [batch, ..., n_classes] (one-hot)
        n_classes = tf.shape(y_pred)[-1]
        # Handle [B, D, H, W, 1] case
        if y_true.shape.rank == y_pred.shape.rank and y_true.shape[-1] == 1:
            y_true = tf.squeeze(y_true, axis=-1)
        # One-hot encode if needed
        if y_true.shape.rank == y_pred.shape.rank - 1:
            y_true = tf.one_hot(tf.cast(y_true, tf.int32), depth=n_classes)
        else:
            tf.debugging.assert_equal(
                tf.shape(y_true)[-1], n_classes,
                message="y_true and y_pred should have same number of channels"
            )
        #---new patch sparse case

        y_true_cls = tf.expand_dims(y_true[..., self.class_id], axis=-1)
        y_pred_cls = tf.expand_dims(y_pred[..., self.class_id], axis=-1)

        dice_loss = self.loss_fn(y_true_cls, y_pred_cls)  # shape: (batch,) or scalar
        dice_score = 1.0 - dice_loss

        #---new patch
        if sample_weight is not None:
            dice_score = dice_score * tf.cast(sample_weight, self.dtype)

        batch_score = tf.reduce_sum(dice_score)
        batch_count = tf.cast(tf.size(dice_score), tf.float32)

        self.dice_sum.assign_add(batch_score)
        self.count.assign_add(batch_count)

    def result(self):
        return self.dice_sum / (self.count + 1e-7)

    def reset_states(self):
        self.dice_sum.assign(0.0)
        self.count.assign(0.0)

    def get_config(self):
        config = super().get_config()
        config.update({
            "target_class_ids": [self.class_id]
        })
        return config
