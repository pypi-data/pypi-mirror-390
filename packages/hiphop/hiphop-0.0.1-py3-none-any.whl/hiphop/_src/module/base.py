from typing import Dict, Any, Callable, Optional, Iterable
import tensorflow as tf


class Module(tf.Module):
    """Base class for all neural network components in HipHop.

    This class serves as a thin, minimal wrapper around `tf.Module`,
    providing a clean and consistent API for defining trainable parameters
    and composing models in an object-oriented manner.

    Each subclass of `Module` should override the `__call__` method to
    implement the forward computation. Variables should be created using
    the `get_variable()` method to ensure consistent naming and management.

    Example:
        ```python
        import hiphop as hh
        import tensorflow as tf

        class Linear(hh.Module):
            def __init__(self, in_features, out_features, name=None):
                super().__init__(name)
                self.w = self.get_variable(
                    "w", [in_features, out_features],
                    initializer=tf.random.normal
                )
                self.b = self.get_variable(
                    "b", [out_features],
                    initializer=tf.zeros
                )

            def __call__(self, x):
                return tf.matmul(x, self.w) + self.b
        ```

    Attributes:
        name (str): Optional name for the module. Used for variable scoping.
    """

    def __init__(self, name=None):
        """Initializes a new HipHop module.

        Args:
            name: Optional string name for the module. If provided, it is used
                as a scope prefix for variables created within this module.
        """
        super().__init__(name)
        

    def _variable_naming(self, prefix: str = "") -> str:
        """Constructs a fully-qualified variable prefix.

        This ensures all variables created inside the module are properly
        namespaced under the module's name.

        Args:
            prefix: Optional prefix string to prepend.

        Returns:
            A fully-qualified name prefix, e.g. `"mlp/dense1/"`.
        """
        return f"{prefix}{self.name}/" if self.name else prefix


    def get_variable(
        self,
        name: str,
        shape=None,
        initializer=lambda **_: None,
        dtype: tf.DType = tf.float32,
        rng=None,
        prefix: str = ""
    ) -> tf.Variable:
        """Creates and registers a trainable variable within the module.

        This is the recommended method to create learnable parameters such as
        weights and biases. It ensures consistent naming, dtype handling, and
        optional RNG seeding for reproducible initialization.

        Args:
            name: Name of the variable (without scope prefix).
            shape: Shape of the variable as a tuple or list. Defaults to `[]`
                for scalars.
            initializer: A callable that returns initial values given keyword
                arguments `(shape, dtype, key)`. The function may optionally
                ignore the `key` argument.
            dtype: TensorFlow data type of the variable (default: `tf.float32`).
            rng: Optional random key or RNG object passed to the initializer.
            prefix: Optional prefix to override the automatic scope naming.

        Returns:
            A `tf.Variable` instance registered under this module.

        Example:
            ```python
            w = self.get_variable("w", [128, 64],
                                  initializer=tf.random.normal)
            ```
        """
        full_name = f"{self._variable_naming(prefix)}{name}"
        shape = shape or []

        try:
            data = initializer(shape=shape, dtype=dtype, key=rng)
        except TypeError:
            # Handle initializers that do not accept `key`
            data = initializer(shape=shape, dtype=dtype)

        var = tf.Variable(data, dtype=dtype, trainable=True, name=full_name)
        setattr(self, name, var)
        return var


    def __call__(self, *args):
        """Defines the forward computation.

        This method must be implemented by subclasses. It is called when
        the module instance is invoked as a function.

        Example:
            ```python
            class MyLayer(hh.Module):
                def __call__(self, x):
                    return x * 2
            ```

        Raises:
            NotImplementedError: If not overridden in a subclass.
        """
        raise NotImplementedError

    # -------------------------------------------------------------------------
    # Variable access
    # -------------------------------------------------------------------------

    @property
    def variables(self):
        """Returns all variables owned by this module and its submodules.

        This property is identical to `tf.Module.variables`, but kept here
        for API consistency within HipHop.

        Returns:
            A list of `tf.Variable` instances.
        """
        variables = super().variables
        return variables

    @property
    def trainable_variables(self):
        """Returns all trainable variables owned by this module and its children.

        This property is identical to `tf.Module.trainable_variables`, but
        exposed here to maintain clarity when writing optimizers and training
        loops.

        Returns:
            A list of trainable `tf.Variable` instances.
        """
        trainable_variables = super().trainable_variables
        return trainable_variables


class Sequential(Module):
    """A container module that applies a sequence of layers in order.

    `Sequential` is a simple utility for chaining together multiple layers or
    modules, where the output of one layer is passed directly as the input
    to the next. It is especially convenient for defining feed-forward
    neural networks such as MLPs.

    Example:
        ```python
        import hiphop as hh
        import tensorflow as tf

        model = hh.Sequential([
            hh.Linear(784, 128),
            tf.nn.relu,
            hh.Linear(128, 64),
            tf.nn.relu,
            hh.Linear(64, 10),
        ])

        x = tf.random.normal([32, 784])
        y = model(x)  # shape: (32, 10)
        ```

    This container does **not** define its own parameters; instead, it holds
    references to submodules and their trainable variables.

    Notes:
    - If the first layer requires extra arguments (e.g., `(x, training=True)`),
      they can be passed through `Sequential.__call__` and will only be applied
      to the first module in the sequence.
    - Each subsequent layer receives only the output of the previous one.

    Args:
        layers: Optional iterable of callables or `Module` instances
            that will be applied in sequence.
        name: Optional name for the module scope.
    """

    def __init__(
        self,
        layers: Optional[Iterable[Callable[..., Any]]] = None,
        name: Optional[str] = None,
    ):
        """Initializes the sequential container and stores the given layers."""
        super().__init__(name=name)
        self._layers = list(layers) if layers is not None else []

    def __call__(self, inputs, *args, **kwargs):
        """Applies each layer in order to the input tensor.

        Args:
            inputs: Input tensor or structure passed to the first layer.
            *args: Additional positional arguments forwarded to the **first** layer only.
            **kwargs: Additional keyword arguments forwarded to the **first** layer only.

        Returns:
            The output of the final layer in the sequence.
        """
        outputs = inputs
        for i, mod in enumerate(self._layers):
            if i == 0:
                # Pass extra arguments only to the first module
                outputs = mod(outputs, *args, **kwargs)
            else:
                outputs = mod(outputs)
        return outputs