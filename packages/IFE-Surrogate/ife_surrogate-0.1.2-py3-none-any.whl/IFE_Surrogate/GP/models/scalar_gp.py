# ------------------------------------------------------------------------------
# Project: IFE_Surrogate
# Authors: Tobias Leitgeb, Julian Tischler
# CD Lab 2025
# ------------------------------------------------------------------------------
from IFE_Surrogate.GP.abstract_gp import AbstractGP
from IFE_Surrogate.GP.train import train, train_scipy
from IFE_Surrogate.GP.likelihood import nlml_scalar
from IFE_Surrogate.GP.inference import predictive_mean_var_scalar
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

Kernel = typing.TypeVar("Kernel", bound=AbstractKernel)

class Scalar_GP(AbstractGP):
    r"""
    Scalar Gaussian Process (GP) model for scalar regression tasks.

    .. math::
        f \thicksim \mathcal{GP}(0, k(x, x'))

    Parameters
    ----------
    X : Array
        Training input data of shape (n_samples, n_features).
    Y : Array
        Training output data of shape (n_samples, 1)
    kernel : Kernel
        Instance of a kernel class defining the covariance structure.
    """
    def __init__(self, X: Array, Y: Array, kernel: Kernel):
        assert X.shape[0] == Y.shape[0] , "X and Y should have the same number of samples"
        assert Y.shape[1] == 1, "Y should be a matrix with shape (N, 1) N: #samples"
        super().__init__(kernel, X, Y)
        self.likelihood = nlml_scalar
        self.jitter = 1e-6
       
    def train(
        self, 
        key: Key,
        optim_dictionary: Dict={"opt": optax.adam, "settings": {"learning_rate": 1e-2}}, 
        n_steps: Int =1000, 
        n_restarts: int=1, 
        save_history: Bool=False, 
        verbose: Bool=False
    ) -> Tuple:
        """
        Optimize kernel parameters by minimizing the negative marginal log-likelihood using gradient-based optimizers.

        Parameters
        ----------
        key : Key
            Random key for parameter initialization and restarts.
        optim_dictionary : Dict, optional
            Dictionary containing the optimizer class (`"opt"`) and its settings (`"settings"`).
        num_steps : int, optional
            Number of optimization steps for each restart.
        number_restarts : int, optional
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
            self, key, optim_dictionary, n_steps, n_restarts, save_history, verbose
        )
        self.kernel.update_params(self.optimized_parameters["params"])

        pass

    def train_scipy(self, 
        key: Key, 
        number_restarts: int=1, 
        opt_algorithm: Dict={"method":"L-BFGS-B"},
        save_history: Bool=False, 
        verbose: Bool=True
    ) -> Tuple:
        """
        Optimize kernel parameters using a scipy-based optimizer (e.g., L-BFGS-B).

        Parameters
        ----------
        key : Key
            Random key for parameter initialization and restarts.
        number_restarts : int, optional
            Number of independent optimization restarts with different initializations.
        opt_algorithm : Dict, optional
            Dictionary specifying the optimization method and settings (e.g., `"method": "L-BFGS-B"`).
        save_history : bool, optional
            If True, saves the full optimization trajectory.
        verbose : bool, optional
            If True, prints optimization progress.

        Returns
        -------
        Tuple
            Optimized parameters and, if requested, parameter history.
        """
        self.optimized_parameters, self.parameter_history = train_scipy(
            self, key, number_restarts, opt_algorithm, save_history, verbose
        )
        self.kernel.update_params(self.optimized_parameters["params"])
    
    def predict(self, X_test: Array) -> Tuple[Array, Array]:
        """
        Predict the mean and variance for the given test inputs.

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
        X_test = jnp.atleast_2d(X_test)
        mean, var = (predictive_mean_var_scalar)(
            self.X, self.Y, self.kernel, self.jitter, X_test 
        )
        return mean, var
   
    def log_marginal_likelihood(self):
        """
        Compute the (negative) log marginal likelihood of the current model.

        Returns
        -------
        float
            The negative log marginal likelihood value.
        """
        return self.likelihood(self.X, self.Y, self.jitter, self.kernel)
    

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



class Scalar_GP_baysian(AbstractGP):
    r"""
    Fully baysian Scalar Gaussian Process (GP) model for scalar regression tasks.

    .. math::
        f \thicksim \mathcal{GP}(0, k(x, x'))

    Parameters
    ----------
    X : Array
        Training input data of shape (n_samples, n_features).
    Y : Array
        Training output data of shape (n_samples, 1)
    kernel : Kernel
        Instance of a kernel class defining the covariance structure.
    """
    def __init__(self, X: Array, Y: Array, kernel: Kernel):
        assert X.shape[0] == Y.shape[0] , "X and Y should have the same number of samples"
        assert Y.shape[1] == 1, "Y should be a matrix with shape (N, 1) N: #samples"
        super().__init__(kernel, X, Y)
        self.jitter = 1e-6
        self.likelihood = nlml_scalar
       
    def model_forward(self,):
        r"""
        Forward pass of the model required for Bayesian inference with NumPyro.

        This function defines the joint distribution over the observations and the kernel hyperparameters. 

        .. math:: 
        
             p(\mathbf{y} \mid \mathbf{X}, \boldsymbol{\theta}) p(\boldsymbol{\theta})

        By specifying priors over hyperparameters and a Gaussian Process likelihood, 
        we enable NumPyro to perform inference and approximate the posterior over kernel parameters:

        .. math::

            p(\boldsymbol{\theta} \mid \mathcal{D}) \propto 
            p(\mathbf{y} \mid \mathbf{X}, \boldsymbol{\theta}) \, p(\boldsymbol{\theta})

        where:

        - :math:`p(\boldsymbol{\theta})` are the user-defined priors over kernel parameters,
        - :math:`p(\mathbf{y} \mid \mathbf{X}, \boldsymbol{\theta})` is the GP marginal likelihood:

        .. math::

            \mathbf{y} \sim \mathcal{N}(\mathbf{0}, K_{\boldsymbol{\theta}} + \sigma^2 I)

        The kernel matrix :math:`K_{\boldsymbol{\theta}}` is computed using the sampled 
        hyperparameters. 
        """
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

        K = self.kernel(self.X, self.X) + self.jitter * jnp.eye(self.X.shape[0])

        numpyro.sample(
            "Y",
            dist.MultivariateNormal(loc=jnp.zeros(self.X.shape[0]), covariance_matrix=K),
            obs=self.Y,
        )

    # def train(self):
    #     pass

#

    def predict(self, samples, X_test: Array) -> Tuple[Array, Array]:
        """
        Predict the mean and variance for the given test inputs.

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
        self.kernel.update_params(samples)
        return predictive_mean_var_scalar(self.X, self.Y, self.kernel,self.jitter, X_test)
         
   
    def log_marginal_likelihood(self):
        """
        Compute the (negative) log marginal likelihood of the current model.

        Returns
        -------
        float
            The negative log marginal likelihood value.
        """
        return self.likelihood(self.X, self.Y, self.jitter, self.kernel)
    

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