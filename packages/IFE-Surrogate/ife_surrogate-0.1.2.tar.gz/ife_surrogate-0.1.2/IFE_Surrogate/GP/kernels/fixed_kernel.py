from flax import struct
import jax.numpy as jnp
from typing import Dict
from jaxtyping import Array
from IFE_Surrogate.GP.kernels.base_kernel import AbstractKernel
from jax.scipy.interpolate import RegularGridInterpolator


@struct.dataclass
class FixedFreqKernel(AbstractKernel):
    """
    Kernel with a learnable spatial part Kx and a *fixed* frequency correlation matrix Cw.
    Kw = diag(alpha) @ Cw @ diag(alpha).
    """
    sigma: Array 
    _C_w: Array = struct.field(pytree_node=False, default_factory=dict)                             # fixed correlation matrix (P, P)
    _priors: Dict[str, callable] = struct.field(pytree_node=False, default_factory=dict)
    _param_bounds: Dict = struct.field(pytree_node=False, default_factory=dict)

    # full evaluate (returns both Kx and Cw)
    def evaluate(self, W1, W2):

        # frequency part (fixed, just slice the known C_w)
        idx1 = jnp.searchsorted(W1.ravel(), W1.ravel())
        idx2 = jnp.searchsorted(W2.ravel(), W2.ravel())
        Cw = self._C_w[jnp.ix_(idx1, idx2)]

        return Cw
    
@struct.dataclass
class FixedFreqKernel(AbstractKernel):
    """
    Kernel with a learnable spatial part Kx and a *fixed* frequency correlation matrix Cw.
    Kw = diag(alpha) @ Cw @ diag(alpha).

    The frequency correlation is interpolated from a reference correlation matrix C_w
    defined on W_ref.
    """
    sigma: Array
    _C_w: Array = struct.field(pytree_node=False)     # fixed correlation matrix (P,P)
    _W_ref: Array = struct.field(pytree_node=False)   # reference frequency grid
    _priors: Dict[str, callable] = struct.field(pytree_node=False, default_factory=dict)
    _param_bounds: Dict = struct.field(pytree_node=False, default_factory=dict)

    def evaluate(self, W1, W2):
        """
        Interpolates Cw(W1, W2) from reference C_w.
        """
        # convert to numpy because RegularGridInterpolator is scipy, not jax
        W1 = jnp.asarray(W1).ravel()
        W2 = jnp.asarray(W2).ravel()
        W_ref = jnp.asarray(self._W_ref)
        C_w = jnp.asarray(self._C_w) 
        C_w += jnp.eye(C_w.shape[0])*self.sigma

        # Build interpolator *locally*, not as a field
        interp = RegularGridInterpolator(
            (W_ref, W_ref),
            C_w,
            bounds_error=False,
            fill_value=None
        )

        # Interpolate
        points = jnp.array([[(w1, w2) for w2 in W2] for w1 in W1]).reshape(-1, 2)
        Cw_eval = interp(points).reshape(len(W1), len(W2))

        # return as jax array for further computation
        return jnp.asarray(Cw_eval) 


