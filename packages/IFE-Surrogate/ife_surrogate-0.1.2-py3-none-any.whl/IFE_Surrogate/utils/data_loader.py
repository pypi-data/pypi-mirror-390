# ------------------------------------------------------------------------------
# Project: IFE_Surrogate
# Authors: Tobias Leitgeb, Julian Tischler
# CD Lab 2025
# ------------------------------------------------------------------------------
from jaxtyping import Array, Key
import jax.random as jr
from typing import Tuple
import jax.numpy as jnp

import jax.numpy as jnp

def train_test_split(
            X: Array,
            Y: Array,
            f: Array,
            dense: bool = False,
            *,
            split: Tuple[float, float, float] = (0.8, 0.2),
            key: Key,
        )-> Tuple[Tuple[Array, Array], Tuple[Array, Array], Tuple[Array, Array]]:
    """
    Splits the dataset into training, testing, and validation sets.
    Parameters:
    -----------
    X : Array
        Input features array.
    Y : Array
        Target values array.
    f : Array
        Additional features array.
    dense : bool, optional
        If True, the input features will be repeated and concatenated with `f` (default is False).
    split : Tuple[float, float, float], optional
        Ratios for splitting the data into training, testing, and validation sets (default is (0.8, 0.2)).
    key : Key
        Random key for shuffling the data.
    Returns:
    ----------
    Tuple[Tuple[Array, Array], Tuple[Array, Array], Tuple[Array, Array]]
        A tuple containing three tuples: (X_train, Y_train), (X_test, Y_test), and (X_val, Y_val).
    """
    n = X.shape[0]
    n_train = int(n * split[0])
    n_test = int(n * split[1])
   

    #shuffle data
    key, subkey = jr.split(key)
    idx = jr.permutation(subkey, n)
    X = X[idx, :]
    Y = Y[idx, :]

    #split data
    X_train, Y_train = jnp.array(X[:n_train, :]), jnp.array(Y[:n_train, :])
    X_test, Y_test = jnp.array(X[n_train:n_train + n_test, :]), jnp.array(Y[n_train:n_train + n_test, :])
    X_val, Y_val = jnp.array(X[n_train + n_test:, :]), jnp.array(Y[n_train + n_test:, :])

    if dense:
        X_train = jnp.repeat(X_train, len(f), axis=0)
        X_train = jnp.concatenate([X_train, jnp.tile(f, len(X_train)//len(f))[:,None]], axis=1)
        X_test = jnp.repeat(X_test, len(f), axis=0)
        X_test = jnp.concatenate([X_test, jnp.tile(f, len(X_test)//len(f))[:,None]], axis=1)
        X_val = jnp.repeat(X_val, len(f), axis=0)
        X_val = jnp.concatenate([X_val, jnp.tile(f, len(X_val)//len(f))[:,None]], axis=1)
        return (X_train, Y_train), (X_test, Y_test), (X_val, Y_val)
    else:
        return (X_train, Y_train), (X_test, Y_test), (X_val, Y_val)
