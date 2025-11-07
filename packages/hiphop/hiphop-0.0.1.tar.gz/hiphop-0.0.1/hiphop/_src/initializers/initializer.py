import tensorflow as tf
from typing import Tuple

class TruncatedNormal:
    def __init__(self, stddev: float = 1.0):
        self.stddev = stddev

    def __call__(self, shape: Tuple[int, ...], dtype: tf.DType = tf.float32) -> tf.Tensor:
        # tf.random.truncated_normal already does the clipping internally
        return tf.random.truncated_normal(shape, mean=0.0, stddev=self.stddev, dtype=dtype)


class VarianceScaling:
    def __init__(self, scale: float = 1.0, mode: str = "fan_in", distribution: str = "truncated_normal"):
        if mode not in {"fan_in", "fan_out", "fan_avg"}:
            raise ValueError(f"Invalid mode {mode}")
        if distribution not in {"truncated_normal", "normal", "uniform"}:
            raise ValueError(f"Invalid distribution {distribution}")

        self.scale = scale
        self.mode = mode
        self.distribution = distribution

    def __call__(self, shape: Tuple[int, ...], dtype: tf.DType = tf.float32) -> tf.Tensor:
        if len(shape) < 2:
            fan_in = fan_out = 1
        else:
            fan_in, fan_out = shape[1], shape[0]

        if self.mode == "fan_in":
            denominator = tf.cast(fan_in, tf.float32)
        elif self.mode == "fan_out":
            denominator = tf.cast(fan_out, tf.float32)
        else:  # fan_avg
            denominator = tf.cast((fan_in + fan_out) / 2.0, tf.float32)

        variance = self.scale / denominator
        stddev = tf.sqrt(variance)

        if self.distribution == "truncated_normal":
            return tf.random.truncated_normal(shape, mean=0.0, stddev=stddev, dtype=dtype)
        elif self.distribution == "normal":
            return tf.random.normal(shape, mean=0.0, stddev=stddev, dtype=dtype)
        elif self.distribution == "uniform":
            limit = tf.sqrt(3.0 * variance)
            return tf.random.uniform(shape, minval=-limit, maxval=limit, dtype=dtype)


class Constant:
    def __init__(self, value: float):
        self.value = value

    def __call__(self, shape: Tuple[int, ...], dtype: tf.DType = tf.float32) -> tf.Tensor:
        return tf.cast(tf.fill(shape, self.value), dtype)
