# ------------------------------------------------------------------------------
# Project: IFE_Surrogate
# Authors: Tobias Leitgeb, Julian Tischler
# CD Lab 2025
# ------------------------------------------------------------------------------

from jaxtyping import Array
from typing import Tuple
import jax.numpy as jnp
from jax import scipy as jsp
from jax import jit


def predictive_mean_var_wideband(
        X_train: Array, 
        Y_train: Array,
        sigma_sq: float,
        kernel ,
        jitter: float,
        X_test: Array,
    ) -> Tuple[Array, Array]:
    r"""
    Calculates the posterior mean and variance for a wideband (multi-output) 
    Gaussian Process with a diagonal noise covariance:
    
    .. math::
    
        p(\mathbf{f_{*,p}}|\mathbf{X},\mathbf{y_p},\mathbf{X_*})  =& \; \mathcal{N}(\mathbf{f_*}|\mathbf{\mu_{p}},\mathbf{\Sigma_p}) \\
        \mathbf{\mu_p}                          =&  \; \mathbf{K_*}^{T}\mathbf{K_x}^{-1} \mathbf{y_p} \\
        \mathbf{\Sigma_p}                       =& \; \sigma_p^2 (\mathbf{K_{**}} - \mathbf{K_*}^{T}\mathbf{K_x}^{-1}\mathbf{K_*})

    Args:
        X_train (Array): Training input data of shape (N, D).
        Y_train (Array): Training output data of shape (N, P).
        sigma_sq (float): Variance of the noise.
        kernel: Kernel function object used to compute covariances.
        jitter (float): Small value added to the diagonal for numerical stability.
        X_test (Array): Test input data of shape (M, D).

    Returns:
        Tuple[Array, Array]:  Posterior mean and variance at the test inputs for every task.
            - posterior mean: shape (M, P)
            - posterior variance: shape (M,)
    """
    
    N = X_train.shape[0]
    K = kernel(X_train, X_train) * sigma_sq
    L = jsp.linalg.cho_factor(K + jitter*jnp.eye(N), lower=True)
    alpha = jsp.linalg.cho_solve(L, Y_train)
    k_star = kernel(X_train, X_test) * sigma_sq
    f_star = jnp.dot(k_star.T, alpha)
    v = jnp.linalg.solve(L[0], k_star)
    var_f_star = kernel(X_test, X_test) * sigma_sq - jnp.dot(v.T, v)
    var_f_star = jnp.diag(var_f_star)
    return f_star, var_f_star

def predictive_mean_var_kron(
        X_train: Array, 
        Y_train: Array,
        kernel,
        jitter: float,
        XW_test: Array,
    ) -> Tuple[Array, Array]:

    """
    Predictive mean for Kron GP with Kw = diag(alpha) Cw diag(alpha). Alpha will be linearly interpolated 
    for predictions. Where alpha test = func(f_test| f_train, std(Y_train))
    """

    N, P = Y_train.shape
    X, W = X_train
    X_test, W_test = XW_test
        # --- compute training alpha and interpolate to test tasks
    alpha_train = jnp.sqrt(jnp.var(Y_train, axis=0, ddof=1)).squeeze()  # shape (P,)
    alpha_test = jnp.interp(W_test, W.ravel(), alpha_train.ravel()).squeeze() # shape (P*,)

    
    K_x, C_w = kernel.evaluate((X, W), (X, W))   # return Kx, Cw
    K_w = (alpha_train[:, None] * C_w) * alpha_train[None, :]


    L_x = jnp.linalg.cholesky(K_x + jitter * jnp.eye(N))
    L_w = jnp.linalg.cholesky(K_w + jitter * jnp.eye(P))# * jnp.eye(P))

    # Step 1: Solve in space
    Kx_s = kernel.kernel_1(X_test, X)
    A = jsp.linalg.cho_solve((L_x, True), Y_train)       # N×P
    A_pred_space = Kx_s @ A                              # N* × P

    # --- Step 2: task solve
    Cw_s = kernel.kernel_2(W_test, W)                               # (P*, P) correlation part
    Kw_s = (alpha_test[:, None] * Cw_s) * alpha_train[None, :]      #scale with alpha

    B = jsp.linalg.cho_solve((L_w, True), A_pred_space.T)  # (P, N*)
    mu_star = (Kw_s @ B).T                         # (N*, P*)

    # predictive variance in two steps
    # space
    V_space = Kx_s @ jsp.linalg.cho_solve((L_x, True), Kx_s.T)  # N* x N*
    # tasks
    V_task = Kw_s @ jsp.linalg.cho_solve((L_w, True), Cw_s.T)  # P* x P*
    # Kronecker approximation: variance at each N* x P* element
    N_test, P_test = X_test.shape[0], W_test.shape[0]
    var_star  = jnp.diag(jnp.kron(V_space, V_task)).reshape(N_test, P_test)

    return mu_star, var_star

def predictive_mean_var_scalar(
        X_train: Array, 
        Y_train: Array,
        kernel ,
        jitter: float,
        X_test: Array,
    ) -> Tuple[Array, Array]:
    r"""
    Calculates the posterior mean and variance for a scalar output GP.
    Posterior distribution with posterior mean and variance:
    
    .. math::
    
        p(\mathbf{f_{*}}|\mathbf{X},\mathbf{y},\mathbf{X_*})  =& \; \mathcal{N}(\mathbf{f_*}|\mathbf{\mu},\mathbf{\Sigma}) \\
        \mathbf{\mu_p}                          =&  \; \mathbf{K_*}^{T}\mathbf{K}^{-1} \mathbf{y} \\
        \mathbf{\Sigma_p}                       =& \; \mathbf{K_{**}} - \mathbf{K_*}^{T}\mathbf{K}^{-1}\mathbf{K_*})

    
    """
    N = X_train.shape[0]
    K = kernel(X_train, X_train)
    L = jsp.linalg.cho_factor(K + jitter*jnp.eye(N), lower=True)
    #predictive mean
    alpha = jsp.linalg.cho_solve(L, Y_train)
    k_star = kernel(X_train, X_test)
    f_star = k_star.T@alpha
    #predictive variance
    v = jnp.linalg.solve(L[0], k_star)
    cov_star = kernel(X_test, X_test) - jnp.dot(v.T, v)
    return f_star, jnp.diag(cov_star)
