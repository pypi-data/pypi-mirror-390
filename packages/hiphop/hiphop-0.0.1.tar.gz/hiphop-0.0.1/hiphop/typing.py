from typing import Protocol, Any
import tensorflow as tf

class Initializer(Protocol):
    """Protocol for weight initializers."""
    def __call__(self, shape: tuple[int, ...], dtype:tf.DType) -> tf.Tensor:
        ...

