from ..._src.module.base import Module
import tensorflow as tf


class Flatten(Module):
    """Flattens the input tensor while preserving leading dimensions.

    This layer reshapes the input tensor such that all dimensions after
    `preserve_dims` are collapsed into a single dimension. Commonly used
    to flatten spatial features before passing to a fully-connected layer.

    Example:
        ```python
        import hiphop as hh
        import tensorflow as tf

        x = tf.random.normal([32, 28, 28, 1])  # (batch, height, width, channels)
        flatten = hh.Flatten(preserve_dims=1)
        y = flatten(x)  # shape: (32, 784)
        ```

    Args:
        preserve_dims: Number of leading dimensions to keep unchanged.
            Remaining dimensions are flattened into one.  
            For example, `preserve_dims=1` keeps the batch dimension intact.
        name: Optional string name for variable scoping.
    """

    def __init__(self, preserve_dims: int = 1, name: str | None = None):
        """Initializes the Flatten module."""
        super().__init__(name)
        self.dim = preserve_dims

    def __call__(self, x: tf.Tensor) -> tf.Tensor:
        """Flattens the input tensor after the specified preserved dimensions.

        Args:
            x: Input tensor of shape `(d0, d1, ..., dn)`.

        Returns:
            A tensor where all dimensions after the first `preserve_dims`
            are flattened into a single dimension.  
            Output shape: `(d0, ..., d_{preserve_dims-1}, prod(d_preserve_dims...dn))`.
        """
        shape = tf.shape(x)
        pre = shape[:self.dim]
        next = shape[self.dim:]
        new_shape = tf.concat([pre, [tf.reduce_prod(next)]], axis=0)
        return tf.reshape(x, new_shape)
