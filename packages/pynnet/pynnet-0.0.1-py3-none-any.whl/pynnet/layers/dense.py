import numpy as np
from .base import layer

class dense(layer):
    """
    A fully connected (dense) layer.
    This layer performs a linear transformation:
    output = input @ weights + bias
    
    Supported weight initialization methods:
    - 'random': Simple random normal initialization scaled by 0.01
    - 'he': He initialization (good for ReLU)
    - 'xavier': Xavier/Glorot initialization (good for tanh/sigmoid)
    - 'lecun': LeCun initialization
    - 'identity': Identity matrix initialization (for square matrices)
    - 'orthogonal': Orthogonal matrix initialization
    
    Supported bias initialization methods:
    - 'zeros': Initialize biases to zero
    - 'ones': Initialize biases to one
    - 'random': Initialize biases from normal distribution
    - 'constant': Initialize biases to a specified constant value
    """
    def __init__(self, input_size, output_size, weight_init='he', bias_init='zeros', bias_constant=0.0):
        """
        Initializes the dense layer.

        Args:
            input_size (int): Size of input features/number of input neurons
            output_size (int): Size of output features/number of output neurons
            weight_init (str): Weight initialization method
            bias_init (str): Bias initialization method
            bias_constant (float): Constant value for bias if bias_init='constant'
        """
        super().__init__()
        
        # Store layer dimensions
        self.input_size = input_size
        self.output_size = output_size

        # Initialize weights
        self.weights = self._initialize_weights(weight_init)
        
        # Initialize biases
        self.biases = self._initialize_biases(bias_init, bias_constant)
    
    def _initialize_weights(self, method):
        """Helper method to initialize weights using various techniques."""
        if method == 'random':
            return np.random.randn(self.input_size, self.output_size) * 0.01
            
        elif method == 'he':
            # He initialization - good for ReLU activation
            # std = sqrt(2/n_in)
            std = np.sqrt(2.0 / self.input_size)
            return np.random.randn(self.input_size, self.output_size) * std
            
        elif method == 'xavier':
            # Xavier/Glorot initialization - good for tanh/sigmoid activation
            # std = sqrt(2/(n_in + n_out))
            std = np.sqrt(2.0 / (self.input_size + self.output_size))
            return np.random.randn(self.input_size, self.output_size) * std
            
        elif method == 'lecun':
            # LeCun initialization
            # std = sqrt(1/n_in)
            std = np.sqrt(1.0 / self.input_size)
            return np.random.randn(self.input_size, self.output_size) * std
            
        elif method == 'identity':
            # Identity matrix initialization (must be square)
            if self.input_size != self.output_size:
                raise ValueError("Identity initialization requires input_size == output_size")
            return np.eye(self.input_size)
            
        elif method == 'orthogonal':
            # Orthogonal initialization
            random_matrix = np.random.randn(self.input_size, self.output_size)
            # Use QR decomposition to get an orthogonal matrix
            q, r = np.linalg.qr(random_matrix)
            # Ensure the signs are consistent
            return q * np.sign(np.diag(r))
            
        else:
            raise ValueError(f"Unsupported weight initialization method: {method}")
    
    def _initialize_biases(self, method, constant=0.0):
        """Helper method to initialize biases using various techniques."""
        if method == 'zeros':
            return np.zeros((1, self.output_size))
            
        elif method == 'ones':
            return np.ones((1, self.output_size))
            
        elif method == 'random':
            return np.random.randn(1, self.output_size) * 0.01
            
        elif method == 'constant':
            return np.full((1, self.output_size), constant)
            
        else:
            raise ValueError(f"Unsupported bias initialization method: {method}")
        

    def forward(self, input_data):
        """
        Performs the forward pass for the dense layer.

        Args:
            input_data (np.array): The input data, with shape (batch_size, input_size).

        Returns:
            np.array: The output of the layer, with shape (batch_size, output_size).
        """
        # Cache the input data, it's needed for the backward pass.
        self.input = input_data
        
        # Compute the output: Y = X.W + b
        self.output = np.dot(self.input, self.weights) + self.biases
        return self.output
    
    def backward(self, output_gradient, learning_rate=None):
        """
        Performs the backward pass (backpropagation) for the dense layer.
        It computes and stores the gradients for the optimizer to use.

        Args:
            output_gradient (np.array): The gradient of the loss with respect to the output of this layer.
            learning_rate (float, optional): Not used, kept for compatibility.

        Returns:
            np.array: The gradient of the loss with respect to the input of this layer.
        """
        # 1. Calculate the gradient of the loss with respect to the weights.
        # dL/dW = dL/dY * dY/dW = output_gradient * X^T
        self.weights_gradient = np.dot(self.input.T, output_gradient)

        # 2. Calculate the gradient of the loss with respect to the biases.
        # dL/dB = dL/dY * dY/dB = output_gradient * 1
        self.biases_gradient = np.sum(output_gradient, axis=0, keepdims=True)

        # 3. Calculate the gradient of the loss with respect to the input.
        # dL/dX = dL/dY * dY/dX = output_gradient @ W^T
        input_gradient = np.dot(output_gradient, self.weights.T)

        return input_gradient
