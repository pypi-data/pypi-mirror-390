# ------------------------------------------------------------------------------
# Project: IFE_Surrogate
# Authors: Tobias Leitgeb, Julian Tischler
# CD Lab 2025
# ------------------------------------------------------------------------------
from typing import Dict, Callable
from dataclasses import dataclass
from jaxtyping import Array
import jax.numpy as jnp
from flax import struct
from IFE_Surrogate.GP.kernels.base_kernel import AbstractKernel


@struct.dataclass
class Matern12(AbstractKernel):
    r"""
    Matérn 1/2 kernel (Exponential kernel).

    Computes the covariance between x1 and x2 as:

    .. math::
        k(\mathbf{x}_1, \mathbf{x}_2) = \exp\left(-\frac{\lVert \mathbf{x}_1 - \mathbf{x}_2 \rVert}{\ell}\right)

    Args:
        lengthscale (Array): Lengthscale controlling the smoothness.
        priors (Dict[str, Callable], optional): Priors for hyperparameters.
    """
    lengthscale: Array
    _priors: Dict[str, Callable] = struct.field(pytree_node=False)
    _param_bounds: Dict = struct.field(pytree_node=False, default_factory=dict)

    def evaluate(self, x1: Array, x2: Array) -> Array:
        """
        Evaluate the Matérn 1/2 kernel.

        Args:
            x1 (Array): Input array of shape (n_samples_1, n_features).
            x2 (Array): Input array of shape (n_samples_2, n_features).

        Returns:
            Array: Kernel matrix of shape (n_samples_1, n_samples_2).
        """
        dist = jnp.sum(jnp.abs(x1[:, None] - x2) / self.lengthscale, axis=-1)
        return jnp.exp(-dist)


@struct.dataclass 
class Matern32(AbstractKernel):
    r"""
    Matérn 3/2 kernel.

    Computes the covariance between x1 and x2 as:

    .. math::
        k(\mathbf{x}_1, \mathbf{x}_2) = \left(1 + \frac{\sqrt{3} \lVert \mathbf{x}_1 - \mathbf{x}_2 \rVert}{\ell} \right)
        \exp\left(-\frac{\sqrt{3} \lVert \mathbf{x}_1 - \mathbf{x}_2 \rVert}{\ell} \right)

    Args:
        lengthscale (Array): Lengthscale controlling the smoothness.
        priors (Dict[str, Callable], optional): Priors for hyperparameters.
    """
    lengthscale: Array 
    _priors: Dict[str, Callable] = struct.field(pytree_node=False)
    _param_bounds: Dict = struct.field(pytree_node=False, default_factory=dict)

    def evaluate(self, x1: Array, x2: Array) -> Array:
        """
        Evaluate the Matérn 3/2 kernel.

        Args:
            x1 (Array): Input array of shape (n_samples_1, n_features).
            x2 (Array): Input array of shape (n_samples_2, n_features).

        Returns:
            Array: Kernel matrix of shape (n_samples_1, n_samples_2).
        """
        dist = jnp.sum(jnp.abs(x1[:, None] - x2) / self.lengthscale, axis=-1)
        return (1.0 + jnp.sqrt(3.0) * dist) * jnp.exp(-jnp.sqrt(3.0) * dist)


@struct.dataclass
class Matern52(AbstractKernel):
    r"""
    Matérn 5/2 kernel.

    Computes the covariance between x1 and x2 as:

    .. math::
        k(\mathbf{x}_1, \mathbf{x}_2) = \left(1 + \frac{\sqrt{5} \lVert \mathbf{x}_1 - \mathbf{x}_2 \rVert}{\ell} + \frac{5 \lVert \mathbf{x}_1 - \mathbf{x}_2 \rVert^2}{3 \ell^2} \right)
        \exp\left(-\frac{\sqrt{5} \lVert \mathbf{x}_1 - \mathbf{x}_2 \rVert}{\ell} \right)


    Produces GP sample paths that are twice differentiable.

    Args:
        lengthscale (Array): Lengthscale controlling the smoothness.
        priors (Dict[str, Callable], optional): Priors for hyperparameters.
    """
    lengthscale: Array 
    _priors: Dict[str, Callable] = struct.field(pytree_node=False)
    _param_bounds: Dict = struct.field(pytree_node=False, default_factory=dict)

    def evaluate(self, x1: Array, x2: Array) -> Array:
        """
        Evaluate the Matérn 5/2 kernel.

        Args:
            x1 (Array): Input array of shape (n_samples_1, n_features).
            x2 (Array): Input array of shape (n_samples_2, n_features).

        Returns:
            Array: Kernel matrix of shape (n_samples_1, n_samples_2).
        """
        scaled_diff = (x1[:, None] - x2) / self.lengthscale
        dist = jnp.sqrt(jnp.sum(scaled_diff**2, axis=-1))
        sqrt5_dist = jnp.sqrt(5.0) * dist
        return (1.0 + sqrt5_dist + (5.0 / 3.0) * dist**2) * jnp.exp(-sqrt5_dist)
