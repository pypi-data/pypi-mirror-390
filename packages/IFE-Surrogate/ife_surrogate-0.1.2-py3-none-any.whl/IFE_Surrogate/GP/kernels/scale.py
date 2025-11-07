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



@struct.dataclass
class Scale(AbstractKernel):
    r"""
    Scale Kernel.

    The Scale kernel is a simple kernel that outputs a constant value across all pairs of points. 
    It is often used in combination with other kernels to add a scaling factor. 

    The kernel is defined as:
    .. math::
       k(\mathbf{x}_1, \mathbf{x}_2) = \sigma_f^2

    Args:
        variance (Array): The variance (scaling factor) for the kernel. 
        priors (Dict[str, Callable], optional): Priors for the hyperparameter (variance).
    """
    variance: Array 
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
        return self.variance * jnp.ones((x1.shape[0], x2.shape[0]))
