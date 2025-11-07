import numpy as np
import time  # Added for verbose epoch timing
from .optimizer import SGD # Import a default optimizer

class sequential:
    """
    A sequential model, which is a linear stack of layers.
    """

    def __init__(self):
        """
        Initializes the model.
        """
        self.layers = []
        self.loss = None
        self.loss_derivative = None
        self.optimizer = None

    def add(self, layer):
        """
        Adds a new layer to the model.
        
        Args:
            layer: An instance of a Layer class (e.g., Dense, Activation).
        """
        self.layers.append(layer)

    def compile(self, loss, loss_derivative, optimizer):
        """
        Configures the model for training.
        
        Args:
            loss (callable): The loss function (e.g., mse).
            loss_derivative (callable): The derivative of the loss function (e.g., mse_derivative).
            optimizer (BaseOptimizer): An instance of an optimizer (e.g., Adam(), SGD()).
        """
        self.loss = loss
        self.loss_derivative = loss_derivative
        self.optimizer = optimizer
        print("Model compiled successfully.")

    def set_loss(self, loss_function, loss_derivative):
        """
        Sets the loss function and its derivative.
        
        NOTE: This is a legacy method. `compile()` is preferred as it
        also sets the optimizer. If this is used, a default SGD
        optimizer will be set.
        """
        self.loss = loss_function
        self.loss_derivative = loss_derivative
        if self.optimizer is None:
            self.optimizer = SGD()
            print("Warning: `set_loss` is deprecated. Use `compile`. Defaulting to SGD optimizer.")

    def predict(self, input_data):
        """
        Generates output predictions for the input samples.
        
        Args:
            input_data (np.ndarray): Input data. Shape should be 
                                     (num_samples, 1, num_input_features) 
                                     to match the training data format.
        
        Returns:
            np.ndarray: An array of predictions. Shape will be
                        (num_samples, 1, num_output_features).
        """
        num_samples = len(input_data)
        results = []

        for i in range(num_samples):
            # Run the forward pass for one sample
            output = input_data[i]
            for layer in self.layers:
                output = layer.forward(output)
            results.append(output)
        
        return np.array(results)

    def fit(self, x_train, y_train, epochs, learning_rate=None, verbose=True, print_every=100):
        """
        Trains the model for a fixed number of epochs.
        
        Args:
            x_train (np.ndarray): Training data. Shape (num_samples, 1, num_input_features).
            y_train (np.ndarray): True labels. Shape (num_samples, 1, num_output_features).
            epochs (int): Number of times to iterate over the entire dataset.
            learning_rate (float, optional): If provided, this will *overwrite* the
                                             learning rate of the compiled optimizer.
            verbose (bool): Whether to print training progress.
            print_every (int): How many epochs to wait before printing progress.
        """
        
        # --- Pre-Training Checks ---
        if self.optimizer is None:
            raise ValueError("Model must be compiled before fitting. Call model.compile(...)")
        if self.loss is None or self.loss_derivative is None:
            raise ValueError("Loss function is not set. Call model.compile(...)")
            
        if learning_rate:
            self.optimizer.learning_rate = learning_rate
            
        num_samples = len(x_train)
        if num_samples == 0:
            print("Warning: Training data is empty.")
            return

        print(f"Starting training for {epochs} epochs...")
        start_time = time.time()

        # --- Epoch Loop ---
        for epoch in range(epochs):
            total_error = 0
            
            # --- Batch Loop (Stochastic: one sample at a time) ---
            for i in range(num_samples):
                
                # Get a single sample
                x_sample = x_train[i]
                y_sample = y_train[i]
                
                # --- 1. Forward Pass ---
                output = x_sample
                for layer in self.layers:
                    output = layer.forward(output)
                
                # --- 2. Compute Loss (Error) ---
                total_error += self.loss(y_sample, output)

                # --- 3. Backward Pass (Backpropagation) ---
                # Start with the gradient of the loss
                gradient = self.loss_derivative(y_sample, output)
                
                # Pass the gradient backward through all layers
                for layer in reversed(self.layers):
                    # The `backward` method of trainable layers (Dense) will
                    # store its gradients. Other layers will just pass it on.
                    # The learning rate param is ignored by layers, so we pass None.
                    gradient = layer.backward(gradient, None) 

                # --- 4. Update Parameters (Optimizer Step) ---
                # Tell the optimizer to increment its timestep (for Adam/RMSprop)
                self.optimizer.step()
                
                # Tell the optimizer to update parameters for all trainable layers
                for layer in self.layers:
                    self.optimizer.update(layer)
            
            # --- End of Epoch: Report Progress ---
            average_error = total_error / num_samples
            
            if verbose and (epoch == 0 or (epoch + 1) % print_every == 0 or (epoch + 1) == epochs):
                elapsed = time.time() - start_time
                print(f"Epoch {epoch + 1}/{epochs} | Error: {average_error:.6f} | Time: {elapsed:.2f}s")
        
        print(f"Training complete. Final Error: {average_error:.6f}")

    def get_parameters(self):
        """
        Retrieves all trainable parameters (weights and biases) from
        all layers that have them.
        
        Returns:
            list: A list of tuples, where each tuple is (weights, biases)
                  for a trainable layer, in order.
        """
        params = []
        for layer in self.layers:
            # Check if the layer is trainable (i.e., has 'weights' attribute)
            if hasattr(layer, 'weights'):
                params.append((layer.weights, layer.biases))
        return params

    def set_parameters(self, params):
        """
        Loads parameters (weights and biases) into the model's
        trainable layers.
        
        Args:
            params (list): A list of (weights, biases) tuples.
        
        Raises:
            ValueError: If the number of parameter sets doesn't match
                        the number of trainable layers, or if shapes mismatch.
        """
        param_iter = iter(params)
        for layer in self.layers:
            if hasattr(layer, 'weights'):
                try:
                    weights, biases = next(param_iter)
                except StopIteration:
                    raise ValueError("Not enough parameter sets to load. "
                                     "Model architecture does not match saved weights.")
                
                # CRITICAL: Check that the shapes match
                if layer.weights.shape != weights.shape:
                    raise ValueError(f"Shape mismatch for weights in layer {type(layer).__name__}. "
                                     f"Expected {layer.weights.shape}, got {weights.shape}.")
                if layer.biases.shape != biases.shape:
                    raise ValueError(f"Shape mismatch for biases in layer {type(layer).__name__}. "
                                     f"Expected {layer.biases.shape}, got {biases.shape}.")
                                     
                # If all checks pass, load the parameters
                layer.weights = weights
                layer.biases = biases
                
        # After the loop, check if there were any extra params left
        try:
            next(param_iter)
            raise ValueError("Too many parameter sets to load. "
                             "Model architecture does not match saved weights.")
        except StopIteration:
            pass # This is the expected outcome

    def save_weights(self, filepath):
        """
        Saves the model's parameters to a .npz file.
        
        Args:
            filepath (str): The path to save the weights file.
                            (e.g., 'my_model.npz')
        """
        if not filepath.endswith('.npz'):
            filepath += '.npz'
            
        params = self.get_parameters()
        
        if not params:
            print("Warning: Model has no trainable parameters to save.")
            return

        # We use numpy.savez to save multiple arrays in one file.
        # We create a dictionary to name each array clearly.
        param_dict = {}
        for i, (w, b) in enumerate(params):
            param_dict[f'layer_{i}_weights'] = w
            param_dict[f'layer_{i}_biases'] = b
            
        np.savez(filepath, **param_dict)
        print(f"Model weights saved to {filepath}")

    def load_weights(self, filepath):
        """
        Loads model parameters from a .npz file.
        
        You must create a model with the *exact same architecture*
        before calling this method.
        
        Args:
            filepath (str): The path to the .npz weights file.
        """
        if not filepath.endswith('.npz'):
            filepath += '.npz'

        try:
            data = np.load(filepath)
        except FileNotFoundError:
            print(f"Error: No weights file found at {filepath}")
            return
        except Exception as e:
            print(f"Error loading weights file: {e}")
            return

        params = []
        i = 0
        # Load arrays in order until we can't find the next layer
        while f'layer_{i}_weights' in data:
            if f'layer_{i}_biases' not in data:
                print(f"Error: Weights file is corrupt. Missing biases for layer {i}.")
                return
                
            w = data[f'layer_{i}_weights']
            b = data[f'layer_{i}_biases']
            params.append((w, b))
            i += 1
            
        if not params:
            print("Error: No layer parameters found in file.")
            return

        try:
            self.set_parameters(params)
            print(f"Model weights loaded successfully from {filepath}")
        except ValueError as e:
            print(f"Error loading weights: {e}")