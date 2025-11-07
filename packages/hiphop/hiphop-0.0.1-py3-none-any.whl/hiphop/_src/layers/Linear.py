from ..._src.module.base import Module
from ..initializers.initializer import Constant, VarianceScaling
import tensorflow as tf
from ...typing import Initializer
from typing import Optional


class Linear(Module):
    """Applies a fully connected linear transformation to the input.

    This layer computes the transformation:

        ```
        y = xW + b
        ```

    where:
    - `W` is a learnable weight matrix of shape `(in_feat, out_feat)`.
    - `b` is an optional learnable bias vector of shape `(out_feat,)`.

    By default:
    - Weights are initialized using a **He-uniform initializer**
      (`VarianceScaling(scale=2.0, mode="fan_in", distribution="uniform")`),
      suitable for ReLU activations.
    - Biases are initialized to zero.

    Example:
        ```python
        import hiphop as hh
        import tensorflow as tf

        # Create a linear layer with 784 input features and 128 output features
        layer = hh.Linear(784, 128)

        # Forward pass with a batch of 32 samples
        x = tf.random.normal([32, 784])
        y = layer(x)  # shape: (32, 128)
        ```

    Args:
        in_feat: Number of input features (size of the last dimension of input).
        out_feat: Number of output features.
        bias: Whether to include a bias term. Defaults to True.
        weight_init: Optional custom initializer for weights.  
            If None, uses He-uniform initialization.
        bias_init: Optional custom initializer for bias.  
            If None, uses a constant zero initializer.
        dtype: TensorFlow data type for parameters. Defaults to `tf.float32`.
        name: Optional string name for variable scoping.
    """

    def __init__(
        self,
        in_feat: int,
        out_feat: int,
        bias: bool = True,
        weight_init: Optional[Initializer] = None,
        bias_init: Optional[Initializer] = None,
        dtype: tf.DType = tf.float32,
        name: Optional[str] = None,
    ):
        """Initializes layer parameters and registers them as TensorFlow variables."""
        super().__init__(name)
        self.bias = bias

        def he_uniform():
            """He-uniform initializer (Kaiming uniform) recommended for ReLU networks."""
            return VarianceScaling(scale=2.0, mode="fan_in", distribution="uniform")

        # Weight initialization
        self.w_init = weight_init or he_uniform()
        self.w = self.get_variable("w", [in_feat, out_feat], self.w_init, dtype=dtype)

        # Optional bias initialization
        if bias:
            self.b_init = bias_init or Constant(0.0)
            self.b = self.get_variable("b", [out_feat], self.b_init, dtype=dtype)

    def __call__(self, x: tf.Tensor) -> tf.Tensor:
        """Applies the linear transformation to the input tensor.

        Args:
            x: Input tensor of shape `[..., in_feat]`.

        Returns:
            A tensor of shape `[..., out_feat]`, the result of the affine transform.
        """
        y = tf.matmul(x, self.w)
        if self.bias:
            y = y + self.b
        return y
