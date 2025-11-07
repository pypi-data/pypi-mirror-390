import jax.numpy as jnp

def zero_mean_unit_var_axis0(Y, eps=1e-8):
    """
    Standardize Y along axis 0 (samples) so each feature/output 
    has zero mean and unit variance.

    Parameters
    ----------
    Y : array, shape (N, P)
        Input data (N samples, P outputs).
    eps : float
        Small constant to avoid division by zero.

    Returns
    -------
    Y_scaled : array, shape (N, P)
        Standardized data.
    mean : array, shape (1, P)
        Mean of each output across samples.
    std : array, shape (1, P)
        Std of each output across samples.
    """
    mean = jnp.mean(Y, axis=0, keepdims=True)
    std = jnp.std(Y, axis=0, keepdims=True)
    Y_scaled = (Y - mean) / (std + eps)
    return Y_scaled, mean, std

def inverse_standardize_axis0(Y_scaled, mean, std, eps=1e-8):
    """
    Backtransform standardized data to original scale.
    """
    return Y_scaled * (std + eps) + mean


class MinMaxScaler:
    def __init__(self, feature_range=(0.0, 1.0), eps=1e-8):
        self.feature_range = feature_range
        self.eps = eps
        self.data_min_ = None
        self.data_max_ = None
        self.scale_ = None
        self.min_ = None

    def fit(self, Y, axis=None):
        """Compute min and max for scaling."""
        Y_min = jnp.min(Y, axis=axis, keepdims=True)
        Y_max = jnp.max(Y, axis=axis, keepdims=True)
        
        self.data_min_ = Y_min
        self.data_max_ = Y_max
        data_range = Y_max - Y_min
        
        fr_min, fr_max = self.feature_range
        self.scale_ = (fr_max - fr_min) / (data_range + self.eps)
        self.min_ = fr_min - Y_min * self.scale_
        return self

    def transform(self, Y):
        """Scale data to the feature range."""
        return Y * self.scale_ + self.min_

    def inverse_transform(self, Y_scaled):
        """Revert back to the original scale."""
        return (Y_scaled - self.min_) / self.scale_