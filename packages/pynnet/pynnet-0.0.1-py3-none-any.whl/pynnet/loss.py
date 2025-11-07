import numpy as np

# --- Regression Loss Functions ---

def mse(y_true, y_pred):
    """
    Mean Squared Error Loss
    """
    return np.mean((y_true - y_pred) ** 2)

def mse_derivative(y_true, y_pred):
    """
    Derivative of Mean Squared Error Loss
    """
    # Gradient is 2 * (y_pred - y_true), averaged over the batch
    return 2 * (y_pred - y_true) / y_true.shape[0]

def mae(y_true, y_pred):
    """
    Mean Absolute Error Loss
    """
    return np.mean(np.abs(y_true - y_pred))

def mae_derivative(y_true, y_pred):
    """
    Derivative of Mean Absolute Error Loss
    """
    # Gradient is sign(y_pred - y_true), averaged over the batch
    return np.sign(y_pred - y_true) / y_true.shape[0]

def huber_loss(y_true, y_pred, delta=1.0):
    """
    Huber Loss (Robust Regression Loss)
    Less sensitive to outliers than MSE.
    """
    error = y_true - y_pred
    abs_error = np.abs(error)
    quadratic = np.minimum(abs_error, delta)
    linear = abs_error - quadratic
    return np.mean(0.5 * quadratic**2 + delta * linear)

def huber_loss_derivative(y_true, y_pred, delta=1.0):
    """
    Derivative of Huber Loss
    """
    error = y_pred - y_true
    abs_error = np.abs(error)
    
    grad = np.where(abs_error <= delta, error, delta * np.sign(error))
    return grad / y_true.shape[0]


# --- Classification Loss Functions ---

def binary_cross_entropy(y_true, y_pred):
    """
    Binary Cross-Entropy Loss
    For binary classification (0 or 1) with a single sigmoid output.
    """
    epsilon = 1e-15  # Avoid log(0)
    y_pred = np.clip(y_pred, epsilon, 1 - epsilon)
    return -np.mean(y_true * np.log(y_pred) + (1 - y_true) * np.log(1 - y_pred))

def binary_cross_entropy_derivative(y_true, y_pred):
    """
    Derivative of Binary Cross-Entropy Loss (w.r.t y_pred)
    """
    epsilon = 1e-15
    y_pred = np.clip(y_pred, epsilon, 1 - epsilon)
    
    # Gradient is (y_pred - y_true) / (y_pred * (1 - y_pred))
    # This simplifies nicely when combined with sigmoid derivative!
    grad = (y_pred - y_true) / (y_pred * (1 - y_pred) + epsilon)
    return grad / y_true.shape[0]

def categorical_cross_entropy(y_true, y_pred):
    """
    Categorical Cross-Entropy Loss
    For multi-class classification.
    Assumes y_true is one-hot encoded and y_pred is softmax probabilities.
    """
    epsilon = 1e-15
    y_pred = np.clip(y_pred, epsilon, 1 - epsilon)
    
    # Select only the probabilities for the true classes
    correct_confidences = np.sum(y_true * y_pred, axis=1)
    
    # Calculate log loss
    log_likelihood = -np.log(correct_confidences)
    return np.mean(log_likelihood)

def cce_derivative(y_true, y_pred):
    """
    Derivative of CCE loss (w.r.t. y_pred, the output of Softmax).
    This is complex and not numerically stable.
    See `cce_derivative_with_softmax` for the proper, simplified version.
    """
    epsilon = 1e-15
    y_pred = np.clip(y_pred, epsilon, 1 - epsilon)
    
    grad = -y_true / y_pred
    return grad / y_true.shape[0]

def cce_derivative_with_softmax(y_true, y_pred):
    """
    "SMART" DERIVATIVE
    This computes the gradient of (CCE Loss + Softmax Activation)
    with respect to the *input* of the Softmax layer (Z).
    
    The gradient dL/dZ simplifies to just (y_pred - y_true).
    
    Use this function as the `loss_derivative` in your network
    if your final layer is the `Softmax` class.
    
    Args:
        y_true: The one-hot encoded true labels.
        y_pred: The predicted probabilities (output of Softmax).
    """
    # The gradient is simply the difference, averaged over the batch.
    return (y_pred - y_true) / y_true.shape[0]