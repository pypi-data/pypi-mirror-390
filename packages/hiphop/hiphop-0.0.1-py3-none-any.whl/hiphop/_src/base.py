VARIABLE_REGISTRY = {}
SCOPE_STACK = []
from ..typing import Initializer
from .._api import export
import tensorflow as tf
from typing import Any, Dict

def clear_scope():
    global VARIABLE_REGISTRY, SCOPE_STACK
    VARIABLE_REGISTRY = {}
    SCOPE_STACK = []

class variable_scope:
    def __init__(self, name, reuse=False, reset=False, dtype='float32'):
        self.name = name
        self.reuse = reuse
        self.reset = reset
        self.dtype = dtype

    def __enter__(self):
        effective_reuse = self.reuse or any(r for _, r in SCOPE_STACK)
        SCOPE_STACK.append((self.name, effective_reuse))

        if self.reset:
            prefix = "/".join(scope for scope, _ in SCOPE_STACK)
            keys_to_remove = [k for k in VARIABLE_REGISTRY if k.startswith(prefix)]
            for k in keys_to_remove:
                del VARIABLE_REGISTRY[k]

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        SCOPE_STACK.pop()

def variables_in_scope(scope_name):
    return {k: v for k, v in VARIABLE_REGISTRY.items() if k.startswith(scope_name + "/")}


class VariableScopeModule(tf.Module):
    def __init__(self):
        super().__init__()
        self.registry = {}

    def get_variable(self, name, shape, initializer, dtype=tf.float32):
        if name not in self.registry:
            self.registry[name] = tf.Variable(
                initializer(shape=shape, dtype=dtype),
                name=name,
                trainable=True
            )
        return self.registry[name]

GLOBAL_SCOPE = VariableScopeModule()

def get_variable(name, shape=None, initializer=lambda **_: None, dtype=tf.float32):
    return GLOBAL_SCOPE.get_variable(name, shape, initializer, dtype)

def get_full_name(name):
    full_scope = "/".join(s for s, _ in SCOPE_STACK)
    return f"{full_scope}/{name}" if full_scope else name

def build(fn):
    built = False
    def wrapper(*args, **kwargs):
        nonlocal built
        if not built:
            result = fn(*args, **kwargs)
            built = True
            return result
        else:
            # Reuse variables: disable reset
            SCOPE_STACK[-1] = (SCOPE_STACK[-1][0], True)
            return fn(*args, **kwargs)
    return wrapper


# def get_variable(name: str, shape=None, initializer:Initializer=lambda: None, dtype:tf.DType=tf.float32, rng=None): #type:ignore

#     shape = shape or []

#     full_scope = "/".join(scope for scope, _ in SCOPE_STACK) if SCOPE_STACK else ""
#     full_name = f"{full_scope}/{name}" if full_scope else name

#     # Determine if reuse is allowed from current scope stack
#     reuse_allowed = any(r for _, r in SCOPE_STACK)

#     # Variable already exists
#     if full_name in VARIABLE_REGISTRY:
#         if not reuse_allowed:
#             raise ValueError(f"Variable {full_name} already exists, but reuse is False")
#         return VARIABLE_REGISTRY[full_name]

#     # Variable does not exist but reuse is requested
#     if reuse_allowed:
#         raise ValueError(f"Variable {full_name} does not exist, cannot reuse")

#     # Otherwise, create a new variable
#     try:
#         data = initializer(shape=shape, dtype=dtype, key=rng)
#     except TypeError:
#         data = initializer(shape=shape, dtype=dtype)

#     out = tf.Variable(data, trainable=True, name=name)
#     VARIABLE_REGISTRY[full_name] = out
#     return out 

