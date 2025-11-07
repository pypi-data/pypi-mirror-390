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


from flax import struct
from typing import Dict
import jax.numpy as jnp
from jaxtyping import Array
from IFE_Surrogate.GP.kernels.base_kernel import AbstractKernel

@struct.dataclass
class SM(AbstractKernel):
    """
    Spectral Mixture kernel (vectorized, JAX-safe).

    variance: shape (Q, D)  -- spectral variances v_qd
    means:    shape (Q, D)  -- spectral means mu_qd
    weights:  shape (Q,)    -- mixture weights w_q
    """
    variance: Array
    means: Array
    weights: Array
    _priors: Dict[str, callable] = struct.field(pytree_node=False)
    _param_bounds: Dict = struct.field(pytree_node=False, default_factory=dict)

    def evaluate(self, x1: Array, x2: Array) -> Array:
        x1 = jnp.asarray(x1)
        x2 = jnp.asarray(x2)
        
        diff = x1[:, None, :] - x2[None, :, :]          # (N1, N2, D)
        var_q = self.variance[:, None, None, :]         # (Q,1,1,D)
        mu_q  = self.means[:, None, None, :]            # (Q,1,1,D)
        
        exp_term = jnp.exp(-2.0 * jnp.pi**2 * jnp.sum(var_q * diff[None, :, :, :]**2, axis=-1))
        cos_term = jnp.cos(2.0 * jnp.pi * jnp.sum(mu_q * diff[None, :, :, :], axis=-1))
        
        K = jnp.sum(self.weights[:, None, None] * exp_term * cos_term, axis=0)
        return K
