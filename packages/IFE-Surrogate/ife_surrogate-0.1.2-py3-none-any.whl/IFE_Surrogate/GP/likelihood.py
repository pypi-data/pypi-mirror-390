# ------------------------------------------------------------------------------
# Project: IFE_Surrogate
# Authors: Tobias Leitgeb, Julian Tischler
# CD Lab 2025
# ------------------------------------------------------------------------------
from typing import Callable, Tuple
import jax.numpy as jnp
import jax.scipy as jsp
from jax import vmap
from jaxtyping import Array, Float

def nmll_wideband(
        X: Array,
        Y: Array,
        sigma_sq: Array,
        jitter: Float,
        kernel: Callable,
    ) -> Float:
    r"""
    Computes the negative marginal log-likelihood (NMLL) for a wideband (multi-output) Gaussian Process model:

    .. math::
        
        -\log p(\mathbf{Y} | \mathbf{X}, \mathbf{\theta}, \mathbf{\sigma}^2) = -\sum_{p=1}^P \log\left( p(\mathbf{y}_p|\mathbf{X}, \mathbf{\theta}, \sigma^2_p) \right)

    with:
    
    .. math::

        p(\mathbf{y}_p|\mathbf{X}, \mathbf{\theta}, \sigma^2_p) = 
        \frac{1}{2} \mathbf{y}_p^\intercal \mathbf{K}^{-1} \mathbf{y}_p 
        + \frac{1}{2} \log\left\lvert \mathbf{K} \right\rvert 
        + \frac{n}{2} \log(2\pi) 
        + \frac{N}{2} \log(\sigma_p^2)

    Args:
        X (Array): Training input data of shape (N, D).
        Y (Array): Training output data of shape (N, P), where P is the number of outputs (tasks).
        sigma_sq (Array): Per-output noise variance, shape (P,).
        jitter (float): Small positive constant added to the diagonal of the kernel matrix for numerical stability.
        kernel (Callable): Kernel function used to compute covariances between inputs.

    Returns:
        Float: The negative marginal log-likelihood value.
    
    Notes:
        This implementation assumes independent noise across outputs (diagonal noise covariance),
        and scales the likelihood calculation accordingly.
    """
    def calc_inner_loops(Y, L):
        """
        Calculate the inner loops of a function.

        Parameters:
        - Y_minus_mean: The difference between Y and the mean value.
        - L: The matrix L.

        Returns:
        - The result of the calculation.
            """
        return 0.5 * jnp.dot((Y).T, jsp.linalg.cho_solve((L, True), Y))
    
    inner_loop = vmap(calc_inner_loops, in_axes=(1, None))
    
    p_ = Y.shape[1]
    N = Y.shape[0]
    K = kernel(X, X)
    L = jsp.linalg.cho_factor(K + jitter*jnp.eye(N), lower=True)[0]
    
    nmll = (N*p_/2 * jnp.log(2*jnp.pi) 
            +  p_ * jnp.sum(jnp.log((jnp.diag(L)))) 
            + N/2 * jnp.sum(jnp.log(sigma_sq))) 
    # print(sigma_sq)
    nmll += jnp.sum(inner_loop(Y, L) * (sigma_sq)**-1) #there was a + jitter for some reason
    # nmll += jnp.sum(inner_loop(Y, L) * sigma_sq**-1)#

            
    return nmll



def nlml_scalar(
        X: Array,
        Y: Array,
        jitter: Float,
        kernel: Callable,
    ) -> Float:
    r"""
    Computes the negative marginal log-likelihood (NMLL) for a scalar-output Gaussian Process model:

    .. math::

        p(\mathbf{y}|\mathbf{X}, \mathbf{\theta}) = 
        \frac{1}{2} \mathbf{y}^\intercal \mathbf{K}^{-1} \mathbf{y}
        + \frac{1}{2} \log\left\lvert \mathbf{K} \right\rvert 
        + \frac{N}{2} \log(2\pi) 
        

    Args:
        X (Array): Training input data of shape (N, D).
        Y (Array): Training output data of shape (N, 1) or (N,).
        sigma_sq (Array): Estimated noise variance, shape (1,) or scalar.
        jitter (float): Small positive constant added to the diagonal of the kernel matrix for numerical stability.
        kernel (Callable): Kernel function used to compute covariances between inputs.

    Returns:
        Float: The negative marginal log-likelihood value.
    
    Notes:
        This function is tailored for standard (single-output) Gaussian Process models,
        assuming a homoskedastic noise model.
    """
    N = X.shape[0]
    K = kernel(X, X)
    L = jsp.linalg.cho_factor(K + jitter*jnp.eye(N), lower=True)
    alpha = jsp.linalg.cho_solve(L, Y)
    nmll = (
        N/2 * jnp.log(2*jnp.pi) 
        +jnp.sum(jnp.log((jnp.diag(L[0])))) 
        +1/2*jnp.dot(Y.T, alpha)
    )
    return nmll.squeeze()


def nmll_kron(
        X: Tuple[Array, Array],
        Y: Array,
        jitter: Float,
        kernel: Callable
    ) -> Float:
    r"""
    Computes the negative marginal log-likelihood (NMLL) for a wideband (multi-output) Gaussian Process model:
    with K_w = diag(alpha)C_w diag(alpha) with aloha = sqrt(sigma**2)
    .. math::
        
        -\log p(\mathbf{Y} | \mathbf{X}, \mathbf{\theta}, \mathbf{\sigma}^2) = -\sum_{p=1}^P \log\left( p(\mathbf{y}_p|\mathbf{X}, \mathbf{\theta}, \sigma^2_p) \right)

    with:
    
    .. math::

        \text{vec}(\mathbf{Y})^\top 
        \left( \mathbf{K}_t^{-1} \otimes \mathbf{K}_x^{-1} \right) 
        \text{vec}(\mathbf{Y})
        &= \mathrm{trace} \left( \mathbf{K}_x^{-1} \, \mathbf{Y} \, \mathbf{K}_t^{-1} \, \mathbf{Y}^\top \right) \\[6pt]
        &= \sum_{i=1}^N \sum_{j=1}^P 
        \left[ \mathbf{K}_x^{-1} \mathbf{Y} \right]_{ij} \;
        \left[ \mathbf{K}_t^{-1} (\mathbf{K}_x^{-1} \mathbf{Y})^\top \right]_{ji}

    Args:
        X (Array): Training input data of shape (N, D).
        Y (Array): Training output data of shape (N, P), where P is the number of outputs (tasks).
        jitter (float): Small positive constant added to the diagonal of the kernel matrix for numerical stability.
        kernel (Callable): Kernel function used to compute covariances between inputs.

    Returns:
        Float: The negative marginal log-likelihood value.
    
    Notes:
        This implementation assumes independent noise across outputs (diagonal noise covariance),
        and scales the likelihood calculation accordingly.
    """
    
    N, P = Y.shape
    X, W = X
    sigma_sq = jnp.var(Y, axis=0,ddof=1)    
    alpha_diag = jnp.diag(jnp.sqrt(sigma_sq))

    K_x, C_w = kernel.evaluate((X, W), (X, W))

    K_w = alpha_diag @ C_w @ alpha_diag
    L_x = jsp.linalg.cho_factor(K_x + jitter)
    L_w = jsp.linalg.cho_factor(K_w + jitter)#* jnp.diag(sigma_sq))

    log_det = P * 2*jnp.sum(jnp.log(jnp.diag(L_x[0]))) \
            + N * 2*jnp.sum(jnp.log(jnp.diag(L_w[0])))
    
    A = jsp.linalg.cho_solve(L_x, Y)      # (N,P)
    M = A.T @ Y                           # (P,P)
    quad_form = jnp.trace(jsp.linalg.cho_solve(L_w, M))


    nmll = 0.5 * (quad_form + log_det + N*P*jnp.log(2*jnp.pi))
    
    return nmll


