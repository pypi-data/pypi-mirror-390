import numpy as np
from .layers.base import layer

# --- Base Activation Layer Class ---

class activation(layer):
    """
    An activation layer applies an activation function element-wise to its inputs.
    """
    def __init__(self, activation, activation_derivative):
        """
        Initializes the activation layer.

        Args:
            activation (callable): The activation function to apply.
            activation_derivative (callable): The derivative of the activation function.
        """
        super().__init__()
        self.activation = activation
        self.activation_derivative = activation_derivative

    def forward(self, input_data):
        """
        Forward pass through the activation layer.
        """
        self.input = input_data
        self.output = self.activation(input_data)
        return self.output

    def backward(self, output_gradient, learning_rate):
        """
        Backward pass through the activation layer.
        (learning_rate is not used as there are no trainable parameters)
        """
        # dL/dX = dL/dY * dY/dX
        # dL/dX = output_gradient * activation_derivative(self.input)
        return output_gradient * self.activation_derivative(self.input)

# --- Softmax Layer Class (Special Case) ---

class softmax(layer):
    """
    A Softmax activation layer.
    This is treated as a separate layer because its backward pass is
    special and is almost always combined with Cross-Entropy loss.
    """
    def forward(self, input_data):
        """
        Computes the softmax activation.
        """
        # Subtract max for numerical stability (prevents overflow)
        exp_values = np.exp(input_data - np.max(input_data, axis=-1, keepdims=True))
        self.output = exp_values / np.sum(exp_values, axis=-1, keepdims=True)
        return self.output

    def backward(self, output_gradient, learning_rate):
        """
        Backward pass for softmax.

        IMPORTANT: This backward method assumes it is being used with
        Categorical Cross-Entropy (CCE) loss. The gradient of (CCE + Softmax)
        simplifies to (self.output - y_true).

        If the 'output_gradient' passed here is *already* (self.output - y_true)
        (e.g., calculated by a smart CCE loss function), then we can just return it.
        
        The provided 'output_gradient' from a simple loss.backward()
        like -(y_true / self.output) is NOT the simplified gradient.
        
        For simplicity in this library, we will assume the loss function
        (e.g., cce_derivative) provides the gradient dL/dY.
        The "true" softmax derivative (Jacobian) is complex.

        A common "hack" for simple libraries is to combine the CCE derivative
        and softmax derivative. If the loss function returns (Y_pred - Y_true),
        this layer just passes it through.

        Let's assume the gradient passed in is `dL/dY`.
        The simplified gradient `dL/dZ` (where Z is input) is (Y_pred - Y_true).
        The `output_gradient` we get is `dL/dY`.
        
        Since we don't have Y_true here, we cannot use the simplified version.
        This highlights a design challenge!
        
        For this library, we'll assume the CCE loss function is "smart"
        and its derivative `cce_derivative_softmax` will return the
        simplified gradient (Y_pred - Y_true), which is actually `dL/dZ`.
        So, this `backward` function will just pass that gradient through.
        """
        # This implementation assumes the gradient it receives
        # is already the simplified (Y_pred - Y_true),
        # which is the gradient w.r.t. the *input* of softmax (Z).
        # See `cce_derivative_with_softmax` in losses.py
        return output_gradient


# --- Collection of Activation Functions and their Derivatives ---
# These functions are passed into the `Activation` class constructor.

# Linear
def linear(x):
    return x

def linear_derivative(x):
    return np.ones_like(x)

# Sigmoid
def sigmoid(x):
    return 1 / (1 + np.exp(-x))

def sigmoid_derivative(x):
    s = sigmoid(x)
    return s * (1 - s)

# Tanh
def tanh(x):
    return np.tanh(x)

def tanh_derivative(x):
    return 1 - np.tanh(x) ** 2

# ReLU (Rectified Linear Unit)
def relu(x):
    return np.maximum(0, x)

def relu_derivative(x):
    return np.where(x > 0, 1, 0)

# Leaky ReLU
def leaky_relu(x, alpha=0.01):
    return np.where(x > 0, x, alpha * x)

def leaky_relu_derivative(x, alpha=0.01):
    return np.where(x > 0, 1, alpha)

# ELU (Exponential Linear Unit)
def elu(x, alpha=1.0):
    return np.where(x > 0, x, alpha * (np.exp(x) - 1))

def elu_derivative(x, alpha=1.0):
    return np.where(x > 0, 1, alpha * np.exp(x))

# Swish (from Google Brain)
def swish(x):
    return x * sigmoid(x)

def swish_derivative(x):
    s = sigmoid(x)
    return s * (1 + x * (1 - s))

# Softplus
def softplus(x):
    return np.log(1 + np.exp(x))

def softplus_derivative(x):
    return 1 / (1 + np.exp(-x)) # This is just sigmoid(x)