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
class Kriging(AbstractKernel):
    r"""
    Kriging kernel (a generalized RBF kernel with a power term).

    Computes the covariance between two inputs x1 and x2 as:
    
    .. math::
        
        k_x(\mathbf x, \mathbf{x'}; \mathbf \theta) = \exp{\left(-\frac{1}{2}\sum_{i=1}^d \frac{1}{l_i^{2}} |x_{i} - x'_{i}|^{\kappa_i}\right)}
    
    where:  
    - `lengthscale` controls the smoothness along each input dimension.
    - `power` exponent of the absolute distance .

    Args:
        lengthscale (Array): Positive scaling factors for each input dimension.
        power (Array): Power applied to the distance; must be > 0.
        priors (Dict[str, Callable], optional): Optional priors for hyperparameters.
    """
    lengthscale: Array 
    power: Array 
    _priors: Dict[str, Callable] = struct.field(pytree_node=False)
    _param_bounds: Dict = struct.field(pytree_node=False, default_factory=dict)

    def evaluate(self, x1: Array, x2: Array) -> Array:
        """
        Evaluate the Kriging kernel between x1 and x2.

        Args:
            x1 (Array): Inputs of shape (n_samples_1, n_features).
            x2 (Array): Inputs of shape (n_samples_2, n_features).

        Returns:
            Array: Kernel matrix of shape (n_samples_1, n_samples_2).
        """
        sq_dist = jnp.sum(jnp.abs(x1[:, None] - x2)**self.power * self.lengthscale**-2, axis=-1)
        return jnp.exp(-0.5 * sq_dist)

    






