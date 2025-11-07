# ------------------------------------------------------------------------------
# Project: IFE_Surrogate
# Authors: Tobias Leitgeb, Julian Tischler
# CD Lab 2025
# ------------------------------------------------------------------------------
from abc import ABC, abstractmethod
from typing import Callable, Dict, Tuple
from jaxtyping import Array, Key

class AbstractKernel(ABC):
    """
    Abstract base class for kernels in Gaussian Process regression.
    """

    def __init__(
            self,
        ) -> None:
        """
        Initialize the kernel.

        Args:
           
        """
        pass
    
    @abstractmethod
    def evaluate(self, x1: Array, x2: Array) -> Array:
        """
        Evaluate the kernel function.

        Args:
            x1: First input data array.
            x2: Second input data array.

        Returns:
            Kernel evaluation between x1 and x2.
        """
        pass

    def __call__(self, x1: Array, x2: Array) -> Array:
        """
        

        Args:
            x1: First input data array.
            x2: Second input data array.

        Returns:
            Kernel evaluation between x1 and x2.
        """
        return self.evaluate(x1, x2)
    
    def get_priors(self):
        """
        Get the kernel parameters.

        Returns:
            A dictionary containing the kernel parameters.
        """
        return self._priors
    
    def get_params(self) -> Dict[str, Array]:
        """
        Get the kernel parameters.

        Returns:
            A dictionary containing the kernel parameters.
        """
        return {x: y for x,y in self.__dict__.items() if not x.startswith("_")}
        

    def sample_hyperparameters(self, key: Key) -> Dict[str, Array]:
        """
        Sample new parameters from the prior distribution.

        Args:
            key: JAX random key.

        Returns:
            A dictionary containing sampled parameters.
        """
        #maybe rewrite this to be more readable
        assert isinstance(key, Array), "key must be a jax random key"
        if self._priors is None:
            print("No priors specified. Returning current parameters.")
            return self.get_params()
        
        ## Old Version
        # param_samples = {x: self._priors[x].sample(key, self.__dict__[x].shape) for x in self.__dict__ if not x.startswith("_")}
        # ## ?? Should be: 
        param_samples = {x: self._priors[x].sample(key, self.__dict__[x].shape) for x in self.__dict__.keys() if not x.startswith("_")}
        return param_samples

    def update_params(self, params: Dict[str, Array]) -> None:
        """
        Update the kernel parameters.

        Args:
            params: A dictionary containing the new parameters.
        """

        for key in params:
            self.__dict__[key] = params[key]

    
