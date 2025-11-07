# HipHop

**A minimal neural network library built on top of TensorFlow — simplicity with full control.**

---

## Overview

HipHop is a lightweight, developer-friendly abstraction over [TensorFlow 2](https://www.tensorflow.org/) that gives you the power of raw `tf.Module` without the boilerplate.

Unlike Keras, which hides too much and enforces rigid patterns, HipHop keeps everything explicit and functional — you control the variables, scopes, and computation.

Think of it as *PyTorch-style flexibility* on top of *TensorFlow’s performance*.

---

## Philosophy

- **Minimalism first** – no hidden layers, no magic.
- **Full transparency** – variables are just `tf.Variable`s.
- **Functional & composable** – integrates cleanly with `tf.function`, `tf.GradientTape`, and JIT compilation.
- **Simplicity over automation** – you decide how the model runs, not a framework.

---

## Quick Example: MNIST MLP

```python
import tensorflow as tf
import hiphop as hh
import time

class MLP(hh.Module):
    def __init__(self, name=None):
        super().__init__(name)
        self.fc1 = hh.Linear(784, 128)
        self.fc2 = hh.Linear(128, 64)
        self.fc3 = hh.Linear(64, 10)

    def __call__(self, x):
        x = hh.Flatten()(x)
        x = tf.nn.relu(self.fc1(x))
        x = tf.nn.relu(self.fc2(x))
        x = self.fc3(x)
        return x

def loss_fn(model, x, y):
    logits = model(x)
    return tf.reduce_mean(
        tf.nn.sparse_softmax_cross_entropy_with_logits(labels=y, logits=logits)
    )

def accuracy(model, x, y):
    logits = model(x)
    preds = tf.argmax(logits, axis=-1)
    return tf.reduce_mean(tf.cast(tf.equal(preds, y), tf.float32))

@hh.jit_compile
def train_step(model, x, y, optimizer):
    with tf.GradientTape() as tape:
        loss = loss_fn(model, x, y)
    grads = tape.gradient(loss, model.trainable_variables)
    optimizer.apply_gradients(zip(grads, model.trainable_variables))
    return loss

@hh.jit_compile
def eval_step(model, x, y):
    return accuracy(model, x, y)

# Example training loop
model = MLP()
optimizer = tf.keras.optimizers.Adam(1e-3)

EPOCHS = 5
for epoch in range(EPOCHS):
    start_time = time.time()
    train_acc = tf.metrics.Mean()
    val_acc = tf.metrics.Mean()
    train_loss = tf.metrics.Mean()

    for x, y in ds_train:
        loss = train_step(model, x, y, optimizer)
        acc = eval_step(model, x, y)
        train_acc.update_state(acc)
        train_loss.update_state(loss)

    for x, y in ds_test:
        acc = eval_step(model, x, y)
        val_acc.update_state(acc)

    print(
        f"Epoch {epoch+1}/{EPOCHS} | "
        f"Loss: {train_loss.result():.4f} | "
        f"Train Acc: {train_acc.result():.4f} | "
        f"Val Acc: {val_acc.result():.4f} | "
        f"{time.time() - start_time:.2f}s"
    )
```
---

## Key Features

- `hh.Module`: Minimal, subclassable replacement for tf.Module.

- `get_variable`: Explicit, name-scoped variable creation.

- Clean integration with tf.GradientTape and tf.function.

- `@hh.jit_compile`: Decorator for XLA-accelerated execution.

- Familiar layer primitives (hh.Linear, hh.Flatten, etc.).

- No hidden training loops — you define the behavior.

---

## Installation

```bash
git clone https://github.com/kandarpa02/hiphop.git
cd hiphop
pip install -e .
```

## Requirements

```
Python >= 3.9
TensorFlow >= 2.15
```
---

## Project Status

**HipHop** is currently in alpha.
The goal is to build a TensorFlow-native framework that is:

- feels like **PyTorch**

- but fully compatible with TensorFlow’s runtime and ecosystem.

## Roadmap

- Parameter grouping & module introspection

- More layers (Conv2D, Dropout, BatchNorm, etc.)

## Author

**Kandarpa Sarkar** |
kandarpaexe@gmail.com 

Developer of **HipHop** — aiming to make TensorFlow flexible again.

---

## License

MIT License