# from typing import Any
# from .base import Module, parametermanager
# from .base import next_module_name, module_name_scope

# class Transformable(Module):
#     """
#     Extention of Module object for functional transformation.
#     See the usage bellow in `inline`
    
#     """
#     def __init__(self, name=None):
#         super().__init__(name)
#         self.tracable = None
    
#     def trace(self):
#         with module_name_scope():
#             if self.tracable is None:
#                 raise RuntimeError("Transformable.trace() called without a tracable function.")
#             decorated = parametermanager(name=self.name, reset=True)(self.tracable)
#             def wrapper(*args):
#                 out, params = decorated(*args)
#                 self._params = params
#                 return out
#             return wrapper

    
#     def initial(self, *args):
#         self.placeholder_output = self.trace()(*args)


# def inline(fun):
#     """
#     inline is a special function for transforming functional module block
#     into an output placholder and parameter generator

#     Args:
#         fun (Callable): functional module to transform.

#     Example:
#         import arrayx.nnx as nnx
#         from arrayx.nnx import relu, Conv2d, Linear

#         @nnx.inline
#         def mlp(x):
#             x = Linear(4)(x)
#             x = relu(x)
#             x = Linear(1)(x)
#             return x

#         x = ax.constant(shape=[4, 8])

#         out, params = mlp(x) # get output node and parameters in one go

#         print('out_node: ',out, '\n')
#         print(params)

#         # out_node:  Array(type='Variable', shape=(4, 1), name='intermediate') 

#         # {'mlp/Linear0/kernel': Array(type='Variable', shape=(4, 8), name='mlp/Linear0/kernel', ndarray=
#         #     [[0.24783671 0.05581582 0.4502859  0.03194952 0.0924716  0.20737052
#         #       0.63964355 0.4989711 ]
#         #      [0.87221706 0.96911824 0.04365349 0.52142274 0.55200493 0.41161108
#         #       0.04596162 0.7247937 ]
#         #      [0.12773407 0.40716016 0.9641676  0.03080463 0.30594897 0.7542356
#         #       0.2855394  0.54409313]
#         #      [0.3338344  0.64232194 0.69246364 0.8431648  0.5278648  0.53055453
#         #       0.02708042 0.6949848 ]]), 'mlp/Linear0/bias': Array(type='Variable', shape=(4,), name='mlp/Linear0/bias', ndarray=
#         #     [0. 0. 0. 0.]), 'mlp/Linear1/kernel': Array(type='Variable', shape=(1, 4), name='mlp/Linear1/kernel', ndarray=
#         #     [[0.24783671 0.05581582 0.4502859  0.03194952]]), 'mlp/Linear1/bias': Array(type='Variable', shape=(1,), name='mlp/Linear1/bias', ndarray=
#         #     [0.])}
#     """
#     def wrapper(*args):
#         with module_name_scope():
#             instance = Transformable(name=fun.__name__)
#             instance.tracable = fun
#             instance.initial(*args)

#             return instance.output, instance.params()
#     return wrapper
