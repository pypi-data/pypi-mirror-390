import tensorflow as tf

def valgrad(fun):
    def wrap(*args):
        with tf.GradientTape() as tape:
            [tape.watch(arg) for arg in args]
            out = fun(*args)
            grads = tape.gradient(out, tape.watched_variables())
        
        return out, grads
    return wrap

def grad(fun):
    def wrap(*args):
        with tf.GradientTape() as tape:
            [tape.watch(arg) for arg in args]
            grads = tape.gradient(fun(*args), tape.watched_variables())
        
        return grads
    return wrap

def jit_compile(fun, jit=True):
    return tf.function(fun, jit_compile=True) if jit else tf.function(fun)