# ------------------------------------------------------------------------------
# Project: IFE_Surrogate
# Authors: Tobias Leitgeb, Julian Tischler
# CD Lab 2025
# ------------------------------------------------------------------------------
from IFE_Surrogate.GP.abstract_gp import AbstractGP
from IFE_Surrogate.GP.train import train, train_scipy, train_swarm
from IFE_Surrogate.GP.likelihood import nmll_wideband, nlml_scalar, nmll_kron
from IFE_Surrogate.GP.inference import predictive_mean_var_wideband, predictive_mean_var_scalar, predictive_mean_var_kron
from IFE_Surrogate.GP.kernels.base_kernel import AbstractKernel

from jaxtyping import Key, Array, Int, Bool
from typing import Tuple, Dict
from functools import partial
from jax import vmap, jit
import typing
import jax.numpy as jnp
import numpyro
import optax
import numpyro.distributions as dist
from numpyro.infer import MCMC, NUTS
import warnings


Kernel = typing.TypeVar("Kernel", bound=AbstractKernel)

class Seperable_Multi_output_GP(AbstractGP):
    """
    .. math::
   :label: eq:nmll-kron
        \begin{aligned}
        &\textbf{Model:}\quad 
        \mathrm{vec}(Y)\;\sim\;\mathcal{N}\!\big(0,\;K_w \otimes K_x\big), \\[6pt]
        &\textbf{NMLL:}\quad
        \mathcal{L}(Y;K_x,K_w)
        \;=\;
        \tfrac{1}{2}\,\mathrm{vec}(Y)^\top
        \big(K_w^{-1}\!\otimes K_x^{-1}\big)\,\mathrm{vec}(Y)
        \;+\;
        \tfrac{1}{2}\log\!\big|K_w\otimes K_x\big|
        \;+\;
        \tfrac{NP}{2}\log(2\pi) \\[6pt]
        &\hspace{3.5em}=\;
        \tfrac{1}{2}\,\mathrm{Tr}\!\big(K_x^{-1}\,Y\,K_w^{-1}\,Y^\top\big)
        \;+\;
        \tfrac{1}{2}\,\Big(P\,\log|K_x| \;+\; N\,\log|K_w|\Big)
        \;+\;
        \tfrac{NP}{2}\log(2\pi).
        \end{aligned}

    Parameters
    ----------
    X : Array
        Training input data of shape (n_samples, n_features).
    Y : Array
        Training output data of shape (n_samples, n_outputs), where each output dimension
        typically corresponds to a different frequency.
    kernel : Kernel
        Instance of a kernel class defining the covariance structure.
    frequency : Array, optional
        Array of frequency values corresponding to the output dimensions. If provided, can
        be used to structure the multi-output modeling more explicitly.
    """
    def __init__(self, X: Array, Y: Array, kernel: Kernel, frequency: Array = None):
        if X is not None and not X[0].shape[0] == Y[0].shape[0]:
            warnings.warn("X and Y should have the same number of samples.", category=UserWarning)
        if Y is not None and not Y.shape[1] > 1:
            warnings.warn("Y should be a matrix with shape (N, p) N: #samples, p: #outputs, disregard this warning if you need an empty model.", category=UserWarning)
        super().__init__(kernel, X, Y)
        self.likelihood = nmll_kron
        #self.sigma_sq = Y.var(axis=0, ddof=1) if Y is not None else None
        self.jitter = 1e-6
        self.frequency = frequency
        

    def train(
        self, 
        key: Key,
        optimizer: Dict = {"opt": optax.adam, "settings": {"learning_rate": 1e-2}, "tolerance": 1e-5, "patience": 20}, 
        sample_parameters: Bool = True,
        n_steps: Int = 1000, 
        n_restarts: int = 1, 
        save_history: Bool = False, 
        verbose: Bool = False
    ) -> Tuple:
        """
        Optax training function:
        Optimize kernel parameters by minimizing the negative marginal log-likelihood using gradient-based optimizers.

        Parameters
        ----------
        key : Key
            Random key for parameter initialization and restarts.
        optimizer : Dict, optional
            Dictionary containing the optimizer class (`"opt"`) and its settings (`"settings"`).
        sample_parameters : Bool
            Initial parameters for optimisation are sampled from the priors. If False then the current value of the hyperparameters is used to start the optimization.
        n_steps : int, optional
            Number of optimization steps for each restart.
        n_restarts : int, optional
            Number of independent optimization restarts with different initializations.
        save_history : bool, optional
            If True, saves the full optimization trajectory (parameter history).
        verbose : bool, optional
            If True, prints optimization progress.

        Returns
        -------
        Tuple
            Optimized parameters and, if requested, parameter history.
        """
        
        self.optimized_parameters, self.parameter_history = train(
            self, key, optimizer, sample_parameters, n_steps, n_restarts, save_history, verbose
        )
        self.kernel.update_params(self.optimized_parameters["params"])


    def train_scipy(self, 
        key: Key, 
        n_restarts: int = 1, 
        optimizer: Dict = {"method": "L-BFGS-B"},
        save_history: Bool = False, 
        verbose: Bool = True
    ) -> None:
        """
        Scipy training function:
        Optimize kernel parameters using a scipy-based optimizer (e.g., L-BFGS-B).

        Parameters
        ----------
        key : Key
            Random key for parameter initialization and restarts.
        n_restarts : int, optional
            Number of independent optimization restarts with different initializations.
        optimizer : Dict, optional
            Dictionary specifying the optimizer method and its settings (e.g., `"method": "L-BFGS-B"`).
            (As defined in scipy: https://docs.scipy.org/doc/scipy/tutorial/optimize.html)
        save_history : bool, optional
            If True, saves the full optimization trajectory.
        verbose : bool, optional
            If True, prints optimization progress.

        Returns
        -------
        None
            The optimized hyperparameters are updated in the kernel.
        """
        self.optimized_parameters, self.parameter_history = train_scipy(
            self, key, n_restarts, optimizer, save_history, verbose
        )
        self.kernel.update_params(self.optimized_parameters["params"])
    

    def train_swarm(self, 
        key: Key, 
        bounds: Tuple[Array, Array],
        n_restarts: int = 1,
        optimizer: Dict = {"c1": 0.5, "c2": 0.3, "w": 0.9},
        n_particles: int = 20,
        n_iterations: int = 100,
        save_history: Bool = False, 
        verbose: Bool = True
    ) -> None:
        """
        Pyswarms training function:
        Optimize kernel parameters using PSO

        Parameters
        ----------
        key : Key
            Random key for parameter initialization and restarts.
        n_restarts : int, optional
            Number of independent optimization restarts with different initializations.
        optimizer : Dict, optional
            Dictionary specifying the optimization settings c1, c2, w as defined in pyswarms
                c1: particles own best position
                c2: global best position
                w: balance between c1, c2
                k: number of neighboring particles to consult
                p: distance metric (1: manhattan, 2: euclidean)
        n_particles : Int, optional
            Number of particles in the swarm.
        save_history : bool, optional
            If True, saves the full optimization trajectory.
        verbose : bool, optional
            If True, prints optimization progress.

        Returns
        -------
        None
            The optimized hyperparameters are updated in the kernel.
        """
        self.optimized_parameters, self.parameter_history = train_swarm(
            self, key, bounds, n_restarts=n_restarts, optimizer=optimizer, n_particles=n_particles, n_iterations=n_iterations,
        )
        self.kernel.update_params(self.optimized_parameters["params"])
    
    
    def predict(self, XW_test: Tuple[Array, Array]) -> Tuple[Array, Array]:
        """
        Predict the mean and variance for the given test inputs.
        .. math::
    
            p(\mathbf{f_{*,p}}|\mathbf{X},\mathbf{y_p},\mathbf{X_*})  =& \; \mathcal{N}(\mathbf{f_*}|\mathbf{\mu_{p}},\mathbf{\Sigma_p}) \\
            \mathbf{\mu_p}                          =&  \; \mathbf{K_*}^{T}\mathbf{K_x}^{-1} \mathbf{y_p} \\
            \mathbf{\Sigma_p}                       =& \; \sigma_p^2 (\mathbf{K_{**}} - \mathbf{K_*}^{T}\mathbf{K_x}^{-1}\mathbf{K_*})

        Parameters
        ----------
        X_test : Tuple(Array, Array)  Input a tuple containing X_test and f_test
            

        Returns
        -------
        Tuple[Array, Array]
            Mean predictions and variances for each output dimension.
            Shapes: (n_test_samples, n_outputs)
        """     
        
        y_pred, var_pred = predictive_mean_var_kron(self.X, self.Y, self.kernel, self.jitter, XW_test)
        return y_pred, var_pred
   
    def log_marginal_likelihood(self):
        """
        Compute the (negative) log marginal likelihood of the wideband model.

         .. math::
        
        -\log p(\mathbf{Y} | \mathbf{X}, \mathbf{\\theta}, \mathbf{\sigma}^2) = -\sum_{p=1}^P \log\\big( p(\mathbf{y}_p|\mathbf{X}, \mathbf{\\theta}, \sigma^2_p) \\big)
        
        Returns
        -------
        float
            The negative log marginal likelihood value.
        """
        return nmll_kron(self.X, self.Y, self.jitter, self.kernel)
    
    #@jit
    def log_likelihood_scalar(self):
        """
        Compute the (negative) log marginal likelihood assuming scalar outputs.

        .. math::
        
           \mathcal{L}_p =  p(\mathbf{y}_p|\mathbf{X}, \mathbf{\theta}, \sigma^2_p)

        Returns
        -------
        Array
            An array containing the value of the log likelihood at every task. If summed over it 
            is the same as the complete log likelihood.
        """
        return vmap(nlml_scalar, in_axes=(None, 1, None, None))(self.X, self.Y, self.jitter, self.kernel)

    def sample_posterior(self, key: Key, X: Array, n_samples: Int) -> Array:
        """
        Sample from the posterior distribution at new input locations.

        Parameters
        ----------
        key : Key
            Random key for sampling.
        X : Array
            Input locations where to sample the posterior.
        n_samples : int
            Number of posterior samples to draw.

        Returns
        -------
        Array
            Posterior samples of shape (n_samples, n_test_samples, n_outputs).
        """
        return NotImplementedError
    def sample_prior(self, key: Key, X: Array, n_samples: Int) -> Array:
            """
            Sample from the prior distribution at new input locations.

            Parameters
            ----------
            key : Key
                Random key for sampling.
            X : Array
                Input locations where to sample the prior.
            n_samples : int
                Number of prior samples to draw.

            Returns
            -------
            Array
                Prior samples of shape (n_samples, n_test_samples, n_outputs).
            """
            return NotImplementedError

    def save(self, path: str):
        """
        Save the model parameters to a file.

        Parameters
        ----------
        path : str
            Path where the model parameters should be saved.
        """
        return NotImplementedError

