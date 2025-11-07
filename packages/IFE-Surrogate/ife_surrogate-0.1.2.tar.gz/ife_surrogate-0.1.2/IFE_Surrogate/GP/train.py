# ------------------------------------------------------------------------------
# Project: IFE_Surrogate
# Authors: Tobias Leitgeb, Julian Tischler
# CD Lab 2025
# ------------------------------------------------------------------------------
import optax
from jax import value_and_grad, jit, random
from typing import Tuple, Dict, Callable
from functools import partial
from jaxtyping import Key, Array, Float, Int, Bool
import numpy as np
import jax.numpy as jnp
from scipy.optimize import minimize
from tqdm import tqdm
import pyswarms as ps
from jax import vmap
from jax.flatten_util import ravel_pytree


def train(
        model: Callable, 
        key: Key, 
        optimizer: Dict,
        sample_parameters: Bool = True,
        number_iterations: Int =10000,
        number_restarts: int=1,
        save_history: Bool=False, 
        verbose: Bool=True,
    ) -> Tuple:
    """
    Trains a model using Optax optimizers with multiple random restarts.

    Args:
        model (Callable): The GP model containing kernel, likelihood, and data (X, Y, etc.).
        key (Key): JAX random key for initialization.
        optimizer (Dict): Dictionary with "opt" (Optax optimizer constructor) and "settings" (hyperparameters).
        sample_parameters(Bool). Flag if a sample of the priors is used as a starting point for the optimisation.
        number_iterations (int): Number of optimization steps per restart.
        number_restarts (int): Number of random restarts.
        save_history (bool): If True, returns all optimization runs' history.
        verbose (bool): If True, prints progress and loss values.

    Returns:
        Tuple: (best_run: Dict, history: Dict or None)
            - best_run: Dictionary containing "params", "loss", and "key" for the best performing restart.
            - history: If save_history is True, dictionary of all runs; otherwise None.
    """
    kernel = model.kernel
    likelihood = model.likelihood
    if "sigma_sq" in model.get_attributes().keys():
        nlml = partial(likelihood, model.X, model.Y, model.sigma_sq, model.jitter)
    else:
        nlml = partial(likelihood, model.X, model.Y, model.jitter)
    
    def loss_fn(params: Dict) -> float:
        kernel.update_params(params)
        return nlml(kernel)

    value_and_grad_fn = value_and_grad(loss_fn)

    opt = optimizer["opt"](**optimizer["settings"])
    tolerance = optimizer["tolerance"]
    patience = optimizer["patience"]

    @jit
    def step(params: Dict, opt_state: Dict) -> Tuple:
        loss, grads = value_and_grad_fn(params)
        updates, opt_state = opt.update(grads, opt_state)
        params = optax.apply_updates(params, updates)
        #print(params)
        return params, opt_state, loss
    
    def loop(params: Dict, opt_state: Dict) -> Tuple:
        best_loss = jnp.inf
        no_improve = 0
        for it in range(number_iterations):
            params, opt_state, loss = step(params, opt_state)

            # Early stopping check
            if loss + tolerance < best_loss:  # improvement found
                best_loss = loss
                no_improve = 0
            else:
                no_improve += 1

            if verbose and it % 50 == 0:
                print(f"Iter {it}: loss={loss:.5f}, best={best_loss:.5f}")

            if no_improve >= patience:
                #if verbose:
                print(f"Stopping early at iter {it}, best loss {best_loss:.5f}")
                break

        return params, opt_state, best_loss
    
    #make several restarts with different initializations
    dict_params = {}
    for _ in (range(number_restarts)):
        _, key = random.split(key) 
        if sample_parameters:
            params = kernel.sample_hyperparameters(key)
        else:
            params = kernel.get_params()
        opt_state = opt.init(params)
        params, opt_state, loss = loop(params, opt_state)
        dict_optimization_run = {"params": params, "loss": loss, "key": key}
        dict_params["run_{}".format(_)] = dict_optimization_run
        if verbose:
            print(f"Loss: {loss}")
    #remove nans
    dict_params = {k: v for k, v in dict_params.items() if not jnp.isnan(v['loss'])}
    best_run = min(dict_params, key=lambda x: dict_params[x]['loss'])
    if verbose:
        print("Best run: ", dict_params[best_run]['loss'])
    if save_history:
        print("All optimization runs saved.")
        return dict_params[best_run], dict_params
    return dict_params[best_run], None
    

def train_scipy( 
        model: Callable, 
        key: Key, 
        number_restarts: int=1, 
        opt_algorithm: Dict={"method":"L-BFGS-B"},
        save_history: Bool=False, 
        verbose: Bool=True
    ) -> Tuple:
    """
    Trains a model using Scipy's minimize function with multiple random restarts.

    Args:
        model (Callable): The GP model containing kernel, likelihood, and data (X, Y, etc.).
        key (Key): JAX random key for initialization.
        number_restarts (int): Number of random restarts.
        opt_algorithm (Dict): Dictionary specifying the optimization method for Scipy minimize.
        save_history (bool): If True, returns all optimization runs' history.
        verbose (bool): If True, prints progress and loss values.

    Returns:
        Tuple: (best_run: Dict, history: Dict)
            - best_run: Dictionary containing "params", "loss", and "key" for the best performing restart.
            - history: Dictionary of all optimization runs.
    """
    kernel = model.kernel
    likelihood = model.likelihood
    if "sigma_sq" in model.get_attributes().keys():
        nlml = partial(likelihood, model.X, model.Y, model.sigma_sq, model.jitter)
    else:
        nlml = partial(likelihood, model.X, model.Y, model.jitter)

    dict_params = {}

    # def array_to_dict(params: Array) -> Dict:
    #     new_params = kernel.get_params()
    #     shapes = jnp.array([values.shape[0] for values in new_params.values()])
    #     for i,name in enumerate(new_params.keys()):
    #         if i == 0:
    #             new_params[name] = params[:shapes[i]]
    #         else:
    #             new_params[name] = params[shapes[i-1]:jnp.sum(shapes[:i+1])]
    #     return new_params

    # function for raveling and unraveling the hyperparameter dictionary of the kernel
    params_template = kernel.get_params()
    _, unravel_fn = ravel_pytree(params_template)

    def loss_fn(flat_params: Array) -> float:
        #params = array_to_dict(params)
        params = unravel_fn(flat_params)
        kernel.update_params(params)
        return nlml(kernel)

    for i in tqdm(range(number_restarts)):
        key, subkey = random.split(key)
        params = kernel.sample_hyperparameters(subkey)
        flat_params, _ = ravel_pytree(params)
     
        res = minimize(
            loss_fn, 
            flat_params,
            **opt_algorithm,
            )
        optimized_params = unravel_fn(res.x)
        dict_optimization_run = {"params": optimized_params, "loss": res.fun, "key": key}
        dict_params["run_{}".format(i)] = dict_optimization_run
        if verbose:
            print(f"Loss: {res.fun}")
    
    dict_params = {k: v for k, v in dict_params.items() if not jnp.isnan(v['loss'])}
    best_run = min(dict_params, key=lambda x: dict_params[x]['loss'])
    print("Best run: ", best_run, ":", dict_params[best_run]['loss'])
    return dict_params[best_run], dict_params



def train_swarm(
        model: Callable,
        key: Key,
        bounds: Tuple[Array, Array],
        optimizer: Dict = {"c1": 0.5, "c2": 0.3, "w": 0.9},
        n_restarts: Int = 1,
        n_particles: Int = 20,
        n_iterations: Int = 100,
        save_history: bool = False,
        verbose: bool = True
    ) -> Tuple:
    """
    Trains a model using PySwarms particle swarm optimizer with multiple random restarts.

    Args:
        model (Callable): The GP model containing kernel, likelihood, and data (X, Y, etc.).
        key (KeyArray): JAX random key for initialization.
        bounds (Tuple(Array, Array)) bounds for the optimization, Arrays must be of shape dimension 
        number_restarts (int): Number of random restarts.
        optimizer (Dict): Optimizer options for PySwarms (c1, c2, w).
        number_particles (int): Number of particles.
        number_iterations (int): Number of iterations.
        save_history (bool): If True, returns all optimization runs' history.
        verbose (bool): If True, prints progress and loss values.

    Returns:
        Tuple: (best_run: Dict, history: Dict)
            - best_run: Dictionary containing "params", "loss", and "key" for the best performing restart.
            - history: Dictionary of all optimization runs.
    """
    kernel = model.kernel
    likelihood = model.likelihood

    if "sigma_sq" in model.get_attributes().keys():
        nlml = partial(likelihood, model.X, model.Y, model.sigma_sq, model.jitter)
    else:
        nlml = partial(likelihood, model.X, model.Y, model.jitter)


    # function for raveling and unraveling the hyperparameter dictionary of the kernel
    dict_params = dict()
    params_template = kernel.get_params()
    raveled_template, unravel_fn = ravel_pytree(params_template)
    dimensions = len(raveled_template)
    
    
    def single_particle_loss(flat_params: Array) -> float:
        #params = array_to_dict(params)
        params = unravel_fn(flat_params)
        kernel.update_params(params)
        return nlml(kernel)
    loss_fn = jit(vmap(single_particle_loss))

    #for i in tqdm(range(n_restarts)):
    key, subkey = random.split(key)

    # Particle Swarm Optimization via PySwarms
    optimizer_ = ps.single.GlobalBestPSO(
        n_particles=n_particles,
        dimensions=dimensions,
        options=optimizer,
        bounds=bounds
    )
    i=1
    best_cost, best_pos = optimizer_.optimize(loss_fn, iters=n_iterations, verbose=True)

    optimized_params= unravel_fn(best_pos)

    dict_optimization_run = {"params": optimized_params, "loss": best_cost, "key": key}
    dict_params[f"run_{i}"] = dict_optimization_run

    #if verbose:
    #    print(f"Run {i}: Loss = {best_cost}")

    # Filter out NaN runs if any
    dict_params = {k: v for k, v in dict_params.items() if not np.isnan(v['loss'])}

    # Find the best run
    best_run = min(dict_params, key=lambda x: dict_params[x]['loss'])
    print("Best run:", best_run, ":", dict_params[best_run]['loss'])

    return dict_params[best_run], dict_params if save_history else {}