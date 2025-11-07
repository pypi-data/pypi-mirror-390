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
class RQ(AbstractKernel):
    r"""
    Rational Quadratic Kernel.

    The covariance function is given by:

    .. math::
        k(\mathbf{x}_1, \mathbf{x}_2) = \left(1 + \frac{\lVert \mathbf{x}_1 - \mathbf{x}_2 \rVert^2}{2\alpha \ell^2} \right)^{-\alpha}


    Args:
        lengthscale (Array): Lengthscale controlling the smoothness of the kernel.
        alpha (float): The alpha parameter, controls the relative scale of large and small lengthscales.
        priors (Dict[str, Callable], optional): Priors for hyperparameters.
    """
    lengthscale: Array 
    alpha: float 
    _priors: Dict[str, Callable] = struct.field(pytree_node=False)
    _param_bounds: Dict = struct.field(pytree_node=False, default_factory=dict)

    def evaluate(self, x1: Array, x2: Array) -> Array:
        """
        Evaluate the Rational Quadratic kernel between x1 and x2.

        Args:
            x1 (Array): Input array of shape (n_samples_1, n_features).
            x2 (Array): Input array of shape (n_samples_2, n_features).

        Returns:
            Array: Kernel matrix of shape (n_samples_1, n_samples_2).
        """
        sq_dist = jnp.sum(jnp.abs(x1[:, None] - x2)**2 / self.lengthscale**2, axis=-1)
        return (1 + 0.5 * sq_dist/self.alpha)**-self.alpha

    



