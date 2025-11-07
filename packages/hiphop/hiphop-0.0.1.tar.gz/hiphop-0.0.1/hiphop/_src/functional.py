import tensorflow as tf

# -------------------------------
# Activation Functions
# -------------------------------
relu = tf.nn.relu
leaky_relu = tf.nn.leaky_relu
gelu = tf.nn.gelu
elu = tf.nn.elu
selu = tf.nn.selu
softplus = tf.nn.softplus
softsign = tf.nn.softsign
sigmoid = tf.nn.sigmoid
tanh = tf.nn.tanh
swish = tf.nn.silu      # alias for SiLU
silu = tf.nn.silu

# -------------------------------
# Softmax & Logits Ops
# -------------------------------
softmax = tf.nn.softmax
log_softmax = tf.nn.log_softmax
sigmoid_cross_entropy_with_logits = tf.nn.sigmoid_cross_entropy_with_logits
softmax_cross_entropy_with_logits = tf.nn.softmax_cross_entropy_with_logits

# -------------------------------
# Normalization Ops
# -------------------------------
batch_normalization = tf.nn.batch_normalization
l2_normalize = tf.nn.l2_normalize
local_response_normalization = tf.nn.local_response_normalization

# -------------------------------
# Pooling
# -------------------------------
max_pool2d = tf.nn.max_pool2d
avg_pool2d = tf.nn.avg_pool2d
max_pool3d = tf.nn.max_pool3d
avg_pool3d = tf.nn.avg_pool3d
global_avg_pool = tf.reduce_mean  # simple alias for convenience

# -------------------------------
# Convolution Ops
# -------------------------------
conv1d = tf.nn.conv1d
conv2d = tf.nn.conv2d
conv3d = tf.nn.conv3d
conv2d_transpose = tf.nn.conv2d_transpose
depthwise_conv2d = tf.nn.depthwise_conv2d
separable_conv2d = tf.nn.separable_conv2d

# -------------------------------
# Dropout
# -------------------------------
dropout = tf.nn.dropout
