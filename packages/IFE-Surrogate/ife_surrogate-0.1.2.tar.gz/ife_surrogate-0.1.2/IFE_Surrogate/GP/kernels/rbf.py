# ------------------------------------------------------------------------------
# Project: IFE_Surrogate
# Authors: Tobias Leitgeb, Julian Tischler
# CD Lab 2025
# ------------------------------------------------------------------------------
from dataclasses import dataclass
from jaxtyping import Array
from typing import Callable, Dict
import jax.numpy as jnp
from IFE_Surrogate.GP.kernels.base_kernel import AbstractKernel
from flax import struct

@struct.dataclass
class RBF(AbstractKernel):
    r"""
    Radial Basis Function (RBF) Kernel:

    .. math::
        
        k(\mathbf{x}_1, \mathbf{x}_2) = \exp\left( -\frac{\lVert \mathbf{x}_1 - \mathbf{x}_2 \rVert^2}{2\ell^2} \right)
    

    Args:
        lengthscale (Array): Lengthscale controlling the smoothness of the kernel.
        priors (Dict[str, Callable], optional): Priors for hyperparameters.
    """
    lengthscale: Array
    _priors: Dict[str, Callable] = struct.field(pytree_node=False)
    _param_bounds: Dict = struct.field(pytree_node=False, default_factory=dict)

    def evaluate(self, x1: Array, x2: Array) -> Array:
        """
        Evaluate the Radial Basis Function (RBF) kernel between x1 and x2.

        Args:
            x1 (Array): Input array of shape (n_samples_1, n_features).
            x2 (Array): Input array of shape (n_samples_2, n_features).

        Returns:
            Array: Kernel matrix of shape (n_samples_1, n_samples_2).
        """
        sq_dist = jnp.sum(jnp.abs(x1[:, None] - x2)**2 * self.lengthscale**-2, axis=-1)
        return 1.0 * jnp.exp(-0.5 * sq_dist)



