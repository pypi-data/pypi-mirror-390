from ..functional import *
from ..module import base
import tensorflow as tf

class ReLU(base.Module):
    """Applies the ReLU (Rectified Linear Unit) activation function.

    Computes:
        y = max(0, x)

    Example:
        ```python
        import hiphop as hh
        import tensorflow as tf

        act = hh.ReLU()
        x = tf.constant([-1.0, 0.0, 2.0])
        y = act(x)  # -> [0.0, 0.0, 2.0]
        ```
    """
    def __init__(self, name=None):
        super().__init__(name)

    def __call__(self, x):
        return relu(x)


class LeakyReLU(base.Module):
    """Applies the Leaky ReLU activation function.

    Computes:
        y = x if x > 0 else alpha * x

    Args:
        alpha: Slope for negative inputs. Defaults to 0.2.
        name: Optional name for the module.
    """
    def __init__(self, alpha=0.2, name=None):
        super().__init__(name)
        self.alpha = alpha

    def __call__(self, x):
        return leaky_relu(x, alpha=self.alpha)


class GELU(base.Module):
    """Applies the Gaussian Error Linear Unit (GELU) activation.

    Formula:
        y = 0.5 * x * (1 + erf(x / sqrt(2)))

    Commonly used in Transformer-based architectures (e.g., BERT).

    Example:
        ```python
        act = hh.GELU()
        y = act(tf.random.normal([4, 128]))
        ```
    """
    def __init__(self, name=None):
        super().__init__(name)

    def __call__(self, x):
        return gelu(x)


class ELU(base.Module):
    """Applies the Exponential Linear Unit (ELU) activation function.

    Computes:
        y = x if x > 0 else alpha * (exp(x) - 1)

    Args:
        alpha: Scale factor for negative inputs. Defaults to 1.0.
        name: Optional name for the module.
    """
    def __init__(self, alpha=1.0, name=None):
        super().__init__(name)
        self.alpha = alpha

    def __call__(self, x):
        y = elu(x)
        if self.alpha != 1.0:
            y = tf.where(x > 0, y, self.alpha * y)
        return y


class SELU(base.Module):
    """Applies the Scaled Exponential Linear Unit (SELU) activation.

    Automatically normalizes mean and variance when used with
    appropriate weight initialization (LeCun normal).

    Formula:
        y = scale * (x if x > 0 else alpha * (exp(x) - 1))

    Example:
        ```python
        act = hh.SELU()
        y = act(tf.random.normal([8, 64]))
        ```
    """
    def __init__(self, name=None):
        super().__init__(name)

    def __call__(self, x):
        return selu(x)


class Softplus(base.Module):
    """Applies the Softplus activation function.

    Computes:
        y = log(1 + exp(x))

    Smooth approximation to ReLU, always differentiable.
    """
    def __init__(self, name=None):
        super().__init__(name)

    def __call__(self, x):
        return softplus(x)


class Softsign(base.Module):
    """Applies the Softsign activation function.

    Computes:
        y = x / (1 + |x|)
    """
    def __init__(self, name=None):
        super().__init__(name)

    def __call__(self, x):
        return softsign(x)


class Sigmoid(base.Module):
    """Applies the Sigmoid activation function.

    Computes:
        y = 1 / (1 + exp(-x))
    """
    def __init__(self, name=None):
        super().__init__(name)

    def __call__(self, x):
        return sigmoid(x)


class Tanh(base.Module):
    """Applies the hyperbolic tangent activation function.

    Computes:
        y = tanh(x)
    """
    def __init__(self, name=None):
        super().__init__(name)

    def __call__(self, x):
        return tanh(x)


class Swish(base.Module):
    """Applies the Swish (SiLU) activation function.

    Computes:
        y = x * sigmoid(x)

    Equivalent to SiLU, used in modern architectures (e.g., EfficientNet).
    """
    def __init__(self, name=None):
        super().__init__(name)

    def __call__(self, x):
        return swish(x)


class SiLU(base.Module):
    """Alias for Swish activation (SiLU = Sigmoid Linear Unit).

    Computes:
        y = x * sigmoid(x)
    """
    def __init__(self, name=None):
        super().__init__(name)

    def __call__(self, x):
        return silu(x)


class Softmax(base.Module):
    """Applies the Softmax function over a given dimension.

    Converts raw logits into normalized probabilities.

    Args:
        axis: Dimension along which to apply softmax (default: -1).

    Example:
        ```python
        act = hh.Softmax()
        y = act(tf.constant([[1.0, 2.0, 3.0]]))
        ```
    """
    def __init__(self, axis=-1, name=None):
        super().__init__(name)
        self.axis = axis

    def __call__(self, x):
        return softmax(x, axis=self.axis)
