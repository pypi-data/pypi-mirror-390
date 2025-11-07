# ------------------------------------------------------------------------------
# Project: IFE_Surrogate
# Authors: Tobias Leitgeb, Julian Tischler
# CD Lab 2025
# ------------------------------------------------------------------------------
import IFE_Surrogate as IFE
from IFE_Surrogate.GP.train import train, train_scipy
from IFE_Surrogate.GP.likelihood import nmll_wideband, nlml_scalar
from IFE_Surrogate.GP.inference import predictive_mean_var_wideband, predictive_mean_var_scalar
from IFE_Surrogate.GP.kernels.base_kernel import AbstractKernel

from jaxtyping import Key, Array, Int, Bool
from typing import Tuple, Dict
from functools import partial
import typing
import jax.numpy as jnp
import jax.random as jr
import optax


#TODO 
class Emm_model():
    """
    Expectation-Maximization Mixture of Gaussian Processes (EMM-GP) model.

    This model partitions frequency-dependent output data into clusters, where each cluster is modeled
    by a separate Gaussian Process (GP) with its own kernel. The EM algorithm alternates between assigning
    frequency points to clusters (E-step) and updating the GP models (M-step) for each cluster.

    The model assumes the data is generated from a mixture of GPs:
    
    .. math::

        p(y_n \mid x_n, f_n) = \sum_{k=1}^{K} \pi_k \, p(y_n \mid x_n, f_n, \\theta_k)

    where:
        - :math:`(x_n, f_n)` is the input and frequency for the :math:`n`-th observation,
        - :math:`\pi_k` is the prior probability (mixture weight) of the :math:`k`-th cluster,
        - :math:`\\theta_k` are the hyperparameters of the :math:`k`-th GP,
        - :math:`K` is the number of GP components.

    The algorithm proceeds by:
    
    **E-step**:
    Assign each frequency index to the cluster with the lowest (negative) log-likelihood:

    .. math::

        z_n = \\arg\min_k \\big( -\log \pi_k - \log p(y_n \mid x_n, f_n, \\theta_k) \\big)

    **M-step**:
    Re-train each GP using only the frequency points currently assigned to it, then re-estimate
    mixture weights :math:`\pi_k` as the normalized cluster sizes.

    **ELBO**:
    At each step, the Evidence Lower Bound (ELBO) is evaluated as:

    .. math::

        \mathcal{L} = \sum_{n=1}^N \log \pi_{z_n} + \log p(y_n \mid x_n, f_n, \\theta_{z_n})

    Attributes:
        X_train (Array): Input features of shape (D, N)
        Y_train (Array): Output observations of shape (D, N)
        f (Array): Frequency vector of shape (N,)
        G (int): Number of GP mixture components
        kernels (list): List of initialized kernel objects
        clustered_gp_models (list): Final trained GP models per cluster
        elbo_history (list): ELBO values per iteration
    """
    def __init__(self, X_train: Array, Y_train: Array, f: Array):
        self.X_train = X_train
        self.Y_train = Y_train
        self.f = f
        pass

    def initialize_kernels(self, kernel_configs: list[Tuple[AbstractKernel, Dict, Dict]] , key:Key):
        """
        Automatically initializes g different GP kernels with given priors and hyperparameters.

        Args:
            g (int): Number of clusters/kernels.
            kernel_configs (list of tuples): Each tuple contains (KernelClass, init_params, priors_dict).
            d (int): Dimension of the input space.
            seed (int): Random seed for reproducibility.

        Returns:
            list: Initialized kernel objects.
        """
        G = len(kernel_configs)
        self.G = G
        keys = jr.split(key, G)
        kernels = []

        for i in range(G):
            KernelClass, init_params, priors = kernel_configs[i]
            
            # Initialize kernel with given hyperparameters
            kernel = KernelClass(**init_params, _priors=priors)  
            
            # Sample and update kernel hyperparameters
            sampled_params = kernel.sample_hyperparameters(keys[i])
            kernel.update_params(sampled_params)  

            kernels.append(kernel)
            self.kernels = kernels
            
    def _e_step(self, pi: Array, gp_models: list):
        #calculate the log likelihood for each frequency postion seperately
        log_likelihoods = jnp.array([gp.log_likelihood_scalar() for gp in gp_models])  # Shape: (K,)
        log_pi = jnp.log(pi)[:, None]
        weighted_likelihoods = log_pi + log_likelihoods  # Shape: (K,)
        #if nan values are present, replace them with inf
        weighted_likelihoods = jnp.where(jnp.isnan(weighted_likelihoods), jnp.inf, weighted_likelihoods)
        cluster_assignments = jnp.argmin(weighted_likelihoods, axis=0)
        return cluster_assignments
    
    @staticmethod
    def compute_elbo(pi: Array, gp_models: list, cluster_assignments: Array):
        """
        ELBO for hard EM:
        Sum over all data points of:
        log π_k + log p(y_n | θ_k), where k is the assigned cluster.
        """
        log_pi = jnp.log(pi + 1e-12)  # add epsilon for numerical stability

        # log-likelihood of each cluster
        log_likelihoods = jnp.array([gp.log_likelihood_scalar() for gp in gp_models])  # shape (K,)

        # For each point n (i.e. each frequency), get the assigned cluster
        elbo_terms = log_pi[cluster_assignments] + log_likelihoods[cluster_assignments]

        return jnp.sum(elbo_terms)


    def _m_step(self, cluster_assignments: Array, gp_models: list, optimizer: Dict, key: Key):
        """Re-train GPs and dynamically reduce K if clusters are empty."""

        G = len(gp_models)
        new_clustered_GPs = []
        new_pi = []
        scoring_gp_models = []

        Y = self.Y_train
        X = self.X_train
        f = self.f
        
        non_empty_clusters = []

        for g in range(G):
            mask = cluster_assignments == g
            if jnp.sum(mask) == 0:
                print(f" Cluster {g} is empty! Removing it...")
                continue  # Skip empty clusters
            #use the datapoints for the clusters
            Y_k = Y[:, mask]
            f_k = f[mask]
            #create a new gp for the cluster
            new_gp = IFE.GP.models.Wideband_GP(kernel=gp_models[g].kernel, X=X, Y=Y_k, frequency=f_k)
            #train the gp for the cluster
            #new_gp.train(key=key, optimizer=optimizer, sample_parameters=False, n_steps=optimizer["n_steps"], n_restarts=optimizer["n_restarts"], verbose=False)
            new_gp.train(key=key, **optimizer)
            trained_kernel = new_gp.kernel
            new_clustered_GPs.append(new_gp)
            #create gp with the trained kernel for the given cluster and use all the Y data ( this gp is for scoring the whole frequency domain for each cluster in the E step)
            scoring_gp = IFE.GP.models.Wideband_GP(kernel=trained_kernel, X=X, Y=Y, frequency=f)
            scoring_gp_models.append(scoring_gp)
            non_empty_clusters.append(g)
            new_pi.append(jnp.sum(mask))

        new_pi = jnp.array(new_pi)
        # Normalize new_pi
        new_pi = (new_pi) / jnp.sum(new_pi)
        
        return new_pi, scoring_gp_models, new_clustered_GPs
    
    def run_emm(self,iterations, key, optimizer={ "opt": optax.adam,"settings": { "learning_rate": 0.01 }, "num_restarts":10, "num_steps":100 }):
        elbo_history = []
        scoring_gp_models = [IFE.GP.models.Wideband_GP(kernel=self.kernels[_], X=self.X_train, Y=self.Y_train, frequency=self.f) for _ in range(self.G)]
        pi = jnp.ones(self.G) / self.G
        cluster_assignments_prev = None
        for i in range(iterations):
            key, training_key = jr.split(key)
            cluster_assignments = self._e_step(pi, scoring_gp_models)
            pi, scoring_gp_models, clustered_gp_models = self._m_step(cluster_assignments, scoring_gp_models, optimizer, training_key)
            if jnp.array_equal(cluster_assignments, cluster_assignments_prev):
                print("Model converged")
                break
            #current_mll = sum([gp.log_marginal_likelihood() for gp in clustered_gp_models])
            elbo = self.compute_elbo(pi, scoring_gp_models, cluster_assignments)
            elbo_history.append(elbo)
            print("Current elbo: ", elbo)
            cluster_assignments_prev = cluster_assignments
            print(cluster_assignments)
        self.clustered_gp_models = clustered_gp_models
        self.elbo_history = elbo_history
    def predict(self, X_test):
        Y_pred = []
        Y_var_pred = []
        f_pred = []
        for k in range(len(self.clustered_gp_models)):
            gp_k = self.clustered_gp_models[k]
            f_pred.append(gp_k.frequency)
            y_pred, y_var = gp_k.predict(X_test)
            Y_pred.append(y_pred)
            Y_var_pred.append(y_var)


        Y_pred = jnp.hstack(Y_pred)
        f_pred = jnp.hstack(f_pred)
        Y_var_pred = jnp.hstack(Y_var_pred)
        #sort y pred such that f is in ascending order
        sort_idx = jnp.argsort(f_pred)
        f_pred = f_pred[sort_idx]
        Y_pred = Y_pred[:,sort_idx] #+ Y_mean[None, :]
        Y_var_pred = Y_var_pred[:,sort_idx]
        return Y_pred, Y_var_pred
    
