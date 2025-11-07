# ------------------------------------------------------------------------------
# Project: IFE_Surrogate
# Authors: Tobias Leitgeb, Julian Tischler
# CD Lab 2025
# ------------------------------------------------------------------------------
from dataclasses import dataclass
from jaxtyping import Array
from typing import Callable, Dict
import jax.numpy as jnp
from flax import struct
from IFE_Surrogate.GP.kernels.base_kernel import AbstractKernel

#TODO
#think about this kernel implementation, maybe change something

@struct.dataclass
class Diag_Noise(AbstractKernel):
    r"""
    Kernel that adds noise to the diagonal .
    The kernel is defined as:
    .. math::
       k(\mathbf{x}_i, \mathbf{x}_j) = \sigma_n^2 \delta_{ij}

    Args:
        variance (Array): The variance (scaling factor) for the kernel. 
        priors (Dict[str, Callable], optional): Priors for the hyperparameter (variance).
    """
    noise: Array 
    _priors: Dict[str, Callable] = struct.field(pytree_node=False)
    _param_bounds: Dict = struct.field(pytree_node=False, default_factory=dict)

    def evaluate(self, x1: Array, x2: Array) -> Array:
        """
        Evaluate the Scale kernel between x1 and x2.

        This kernel returns a constant value, which is the variance, for all pairs of points in x1 and x2.

        Args:
            x1 (Array): Input array of shape (n_samples_1, n_features).
            x2 (Array): Input array of shape (n_samples_2, n_features).

        Returns:
            Array: Kernel matrix of shape (n_samples_1, n_samples_2), where each element is the `variance`.
        """
        if x1.shape[0] == x2.shape[0]:
            return self.noise * jnp.eye(x1.shape[0])
        else: 
            return 0.
        

