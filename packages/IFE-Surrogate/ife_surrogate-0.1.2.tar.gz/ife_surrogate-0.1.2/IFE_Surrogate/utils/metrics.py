# ------------------------------------------------------------------------------
# Project: IFE_Surrogate
# Authors: Tobias Leitgeb, Julian Tischler
# CD Lab 2025
# ------------------------------------------------------------------------------
import jax.numpy as jnp
from jax import vmap
from jaxtyping import Array

def nrms(test_y: Array, prediction: Array)-> Array:
        r"""
        Calculates the Normalized Root Mean Square Error.

        .. math:: 

            \text{NRMS} = \frac{\sqrt{\frac{1}{N}\sum_{i=1}^{N} (y_i - \hat{y}_i)^2}}{\max(y) - \min(y)}

        Args:
            test_y (ndarray): The true output values of shape (n, p).
            prediction (ndarray): The predicted output values of shape (n, p).

        Returns:
            float: The Root Mean Square Percentage Error.
        """
        test_y = jnp.atleast_2d(test_y)
        prediction = jnp.atleast_2d(prediction)

        assert test_y.shape == prediction.shape, "test_y and prediction must have the same shape"

        p = test_y.shape[1]
        error = (
            jnp.sqrt(1 / p * jnp.sum((test_y - prediction) ** 2, axis=1))
            / (jnp.max(test_y, axis=1) - jnp.min(test_y, axis=1)) 
        )
        return error

def rmse(test_y: Array, prediction: Array)-> Array:
        r"""
        Calculates the Root Mean Square Error.

        .. math:: 

            RMSPE = \sqrt{\frac{1}{n} \sum_{i=1}^{n} \left( \frac{y_i - \hat{y}_i}{y_i} \right)^2} 
        Args:
            test_y (ndarray): The true output values of shape (n, p).
            prediction (ndarray): The predicted output values of shape (n, p).

        Returns:
            Array: The Root Mean Square Error. 
        """
        test_y = jnp.atleast_2d(test_y)
        prediction = jnp.atleast_2d(prediction)

        assert test_y.shape == prediction.shape, "test_y and prediction must have the same shape"
        p = test_y.shape[1]
        error = jnp.sqrt(1 / p * jnp.sum(((test_y - prediction)/test_y) ** 2, axis=1))
        return error

        