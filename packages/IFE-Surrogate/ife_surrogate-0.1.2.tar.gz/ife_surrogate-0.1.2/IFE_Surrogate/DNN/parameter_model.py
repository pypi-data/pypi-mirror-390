
# ------------------------------------------------------------------------------
# Project: IFE_Surrogate
# Authors: Tobias Leitgeb, Julian Tischler
# CD Lab 2025
# ------------------------------------------------------------------------------
from flax import nnx
from jaxtyping import Array

class ParameterModel(nnx.Module):
    """
    A simple neural network model for predicting a set of parameters.

    This model takes an input of a given dimension and predicts a set of parameters. 
    It consists of three linear layers with ReLU activations. The model architecture 
    is as follows:

        input_dim -> Linear(64) -> ReLU -> Linear(64) -> ReLU -> Linear(num_parameters)

    Args:
        input_dim (int): The dimension of the input data.
        num_parameters (int): The number of parameters that the model will predict.
        rngs (nnx.Rngs): Random number generators for initializing the weights.
    """
    def __init__(
            self, 
            input_dim: int, 
            num_parameters: int, 
            *,
            rngs: nnx.Rngs):
        # Initialize the layers
        self.num_parameters = num_parameters
        self.linear1 = nnx.Linear(input_dim, 64, rngs=rngs)
        self.linear2 = nnx.Linear(64, 64, rngs=rngs)
        self.linear3 = nnx.Linear(64, num_parameters, rngs=rngs)

    def __call__(self, x: Array) -> Array:
        """
        Forward pass of the model.

        Args:
            x (Array): Input data of shape (batch_size, input_dim).

        Returns:
            Array: Predicted parameters of shape (batch_size, num_parameters).
        """
        x = nnx.relu(self.linear1(x))  # First linear layer with ReLU
        x = nnx.relu(self.linear2(x))  # Second linear layer with ReLU
        return self.linear3(x)         # Output layer
