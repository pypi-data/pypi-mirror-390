# ------------------------------------------------------------------------------
# Project: IFE_Surrogate
# Authors: Tobias Leitgeb, Julian Tischler
# CD Lab 2025
# ------------------------------------------------------------------------------
from IFE_Surrogate.GP.abstract_gp import AbstractGP
from IFE_Surrogate.GP.train import train, train_scipy, train_swarm
from IFE_Surrogate.GP.likelihood import nmll_wideband, nlml_scalar
from IFE_Surrogate.GP.inference import predictive_mean_var_wideband, predictive_mean_var_scalar
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

class Wideband_GP(AbstractGP):
    """
    Wideband Gaussian Process (GP) model for multi-output regression tasks.

    This GP handles multiple correlated outputs across a frequency domain, where the 
    outputs can be thought of as different frequency points.

    .. math::

        f \sim \mathcal{GP}(\mathbf{0}, \sigma_i^2 \otimes k(x, x'))

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
        if X is not None and not X.shape[0] == Y.shape[0]:
            warnings.warn("X and Y should have the same number of samples.", category=UserWarning)
        if Y is not None and not Y.shape[1] > 1:
            warnings.warn("Y should be a matrix with shape (N, p) N: #samples, p: #outputs, disregard this warning if you need an empty model.", category=UserWarning)
        super().__init__(kernel, X, Y)
        self.likelihood = nmll_wideband
        self.sigma_sq = Y.var(axis=0, ddof=1) if Y is not None else None
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
    
    
    def predict(self, X_test: Array) -> Tuple[Array, Array]:
        """
        Predict the mean and variance for the given test inputs.
        .. math::
    
            p(\mathbf{f_{*,p}}|\mathbf{X},\mathbf{y_p},\mathbf{X_*})  =& \; \mathcal{N}(\mathbf{f_*}|\mathbf{\mu_{p}},\mathbf{\Sigma_p}) \\
            \mathbf{\mu_p}                          =&  \; \mathbf{K_*}^{T}\mathbf{K_x}^{-1} \mathbf{y_p} \\
            \mathbf{\Sigma_p}                       =& \; \sigma_p^2 (\mathbf{K_{**}} - \mathbf{K_*}^{T}\mathbf{K_x}^{-1}\mathbf{K_*})

        Parameters
        ----------
        X_test : Array
            Test input data of shape (n_test_samples, n_features).

        Returns
        -------
        Tuple[Array, Array]
            Mean predictions and variances for each output dimension.
            Shapes: (n_test_samples, n_outputs)
        """ 
        pred_wideband = partial(predictive_mean_var_wideband, self.X, kernel=self.kernel, jitter=self.jitter, X_test=X_test)
        sigma_sq = jnp.var(self.Y, axis=0, ddof=1)
        mean, var = vmap(pred_wideband, in_axes=(1,0))(self.Y, sigma_sq)
        return mean.T, var.T
   
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
        return nmll_wideband(self.X, self.Y, self.sigma_sq, self.jitter, self.kernel)
    
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


class Wideband_gp_baysian(AbstractGP):
    """
    Bayesian Wideband Gaussian Process model using MCMC sampling.

    This model leverages full Bayesian inference over the kernel parameters
    using Hamiltonian Monte Carlo (HMC) sampling with the NUTS algorithm.

    Parameters
    ----------
    kernel : Kernel
        Kernel object specifying the covariance structure.
    X : Array
        Training input data of shape (n_samples, n_features).
    Y : Array
        Training output data of shape (n_samples, n_outputs).
    """
    def __init__(self, X, Y, kernel):
        super().__init__(kernel, X, Y)
        self.likelihood = nmll_wideband
        self.sigma_sq = Y.var(axis=0)
        self.jitter = 1e-6
    
    def model_forward(self,):
        """
        Defines the probabilistic model for Bayesian inference.

        Samples kernel parameters from their priors and defines the joint likelihood
        over all output frequencies under a multivariate normal distribution.

        Notes
        -----
        - Assumes that the data variance per output is known and fixed.
        - Kernel parameters (like "power" and "lengthscale") are sampled from priors.
        """
        n,p,d=self.X.shape[0], self.Y.shape[1], self.X.shape[1]
        parameters = self.kernel.get_params() #dictionary of all hyperparamers
        hyperparameters = parameters.keys() #list of names of hyperparameters
        prior_functions = self.kernel.get_priors() #dictionary of all prior functions

        for hyperparam_name in hyperparameters:
            n_features = parameters[hyperparam_name].shape #extracts the dimension of the hperparam. e.g ard kernel
            sampled_hyperparam = numpyro.sample(
                hyperparam_name, prior_functions[hyperparam_name].expand(n_features)
            )
            #new sampled hyperparam is put into the dictionary
            parameters[hyperparam_name] = sampled_hyperparam.copy()
            self.kernel.update_params(parameters)#kernel is updated

        
        K = self.kernel(self.X, self.X) + jnp.eye(n) * self.jitter
        
        normal = dist.MultivariateNormal(jnp.zeros(n), K)
        #here again we make the assumption that we dont need to use the variance as a hyperparameter,
        #but just use the data variance
        data_variances = jnp.var(self.Y, axis=0)

        with numpyro.plate("frequency_positions", p): #plate 
            #here I use a little trick so we do not have to calculate the normal distribution for each task
            # N(0, sigma^2) = N(0, 1) / sigma
            obs = self.Y/jnp.sqrt(data_variances)
            for i in range(p):
                numpyro.sample(
                    f"Y{i}", 
                    normal, 
                    obs=obs[:, i], 
                )


    def train(self, key: Key, num_samples:Int = 100, num_warmup:Int = 100):
        """
        Run MCMC to sample from the posterior distribution of the kernel parameters.

        Parameters
        ----------
        key : Key
            Random key for MCMC sampling.
        num_samples : int, optional
            Number of MCMC samples to collect after warm-up.
        num_warmup : int, optional
            Number of warm-up (burn-in) steps before sampling.

        Returns
        -------
        None
            Updates the model's `samples` attribute with posterior samples.
        """
        nuts_kernel = NUTS(self.model_forward)
        mcmc = MCMC(nuts_kernel, num_warmup=num_warmup, num_samples=num_samples)
        mcmc.run(key)
        mcmc.print_summary()
        samples = mcmc.get_samples()
        self.samples = samples


    def predict(self, X_test: Array):
        """
        Predict mean and variance at test points using posterior samples.

        For each posterior sample of the kernel parameters, predictions are made
        and aggregated.

        Parameters
        ----------
        X_test : Array
            Test input data of shape (n_test_samples, n_features).

        Returns
        -------
        Tuple[Array, Array]
            - Mean predictions for each MCMC sample: (n_samples, n_test_samples, n_outputs).
            - Variances for each MCMC sample: (n_samples, n_test_samples, n_outputs).
        """
        pred_one_sample = partial(predictive_mean_var_wideband, self.X, jitter=self.jitter, X_test=X_test)
        #calculates the prediction over the whole frequency axis
        vmap_over_frequency = vmap(pred_one_sample, in_axes=(1,0, None), out_axes=(1,1))

        def wrapper(params):
            self.kernel.update_params(params)
            return vmap_over_frequency(self.Y, self.sigma_sq, self.kernel)
        #calculates the predictions for every generated sample in self.samples
        y_pred_samples, y_var_samples = vmap(wrapper)(self.samples)

        return y_pred_samples, y_var_samples
        
    


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

