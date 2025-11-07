# ------------------------------------------------------------------------------
# Project: IFE_Surrogate
# Authors: Tobias Leitgeb, Julian Tischler
# CD Lab 2025
# ------------------------------------------------------------------------------

from jax import random
import numpy as np
import matplotlib.pyplot as plt
import jax.numpy as jnp

import IFE_Surrogate as IFE


class Evaluator():
    def __init__(self, model=None, kernel=None, X=None, Y=None, f=None):
        self.model = model
        self.kernel = kernel
        self.X = X
        self.Y = Y
        self.f = f
        self.error_functions = {
            "MAE": {"fn": self.mean_absolute_error, "e": []}, 
            "MSE": {"fn": self.mean_squared_error, "e": []},
            "RMSE": {"fn": self.root_mean_squared_error, "e": []}, 
            "SMAPE": {"fn": self.symmetric_mean_absolute_percentage_error, "e": []}, 
            "R2-Score": {"fn": self.r2_score, "e": []}
            }
    
    def _add_error_fn(self, fn):
        fn_name = getattr(fn, "__name__", f.__class__.__name__)
        if not isinstance(fn_name, str):
            raise ValueError("Invalid error function.")
        self.error_functions[fn_name] = {"fn": fn, "e": []}
        

    @staticmethod
    def mean_absolute_error(y_true, y_pred):
        return np.mean(np.abs(y_true - y_pred))

    @staticmethod
    def mean_squared_error(y_true, y_pred):
        return np.mean((y_true - y_pred) ** 2)

    @staticmethod
    def root_mean_squared_error(y_true, y_pred):
        return np.sqrt(np.mean((y_true - y_pred) ** 2))

    @staticmethod
    def mean_absolute_percentage_error(y_true, y_pred):
        y_true = np.where(y_true == 0, np.finfo(float).eps, y_true)
        return np.mean(np.abs((y_true - y_pred) / y_true)) * 100

    @staticmethod
    def symmetric_mean_absolute_percentage_error(y_true, y_pred):
        denominator = (np.abs(y_true) + np.abs(y_pred)) / 2
        denominator = np.where(denominator == 0, np.finfo(float).eps, denominator)
        return np.mean(np.abs(y_true - y_pred) / denominator) * 100

    @staticmethod
    def r2_score(y_true, y_pred):
        ss_res = np.sum((y_true - y_pred) ** 2)
        ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
        return 1 - (ss_res / ss_tot)
    

    def print_errors(self):
        txt = [f"\n----------------------------------------------\n Error function | Average | Minimum | Maximum \n----------------+---------+---------+---------"]

        for k, v in self.error_functions.items():
            errors = np.array(v["e"])
            errors = errors[np.isfinite(errors)]
            avg = errors.mean() if len(errors) > 0 else "-"
            maxi = errors.max() if len(errors) > 0 else "-"
            mini = errors.min() if len(errors) > 0 else "-"

            txt.append(f"{k:^16}|{avg:^9.3f}|{mini:^9.3f}|{maxi:^9.3f}")
        print("\n".join(txt) + "\n")


    def cross_validate(self, error_fn=[], split=(0.4, 0.6), k=5, num_steps=100, num_restarts=10, model_jitter=1e-6, seed=1):
        """Performs k-fold cross validation on the initialized model, kernel and data

        Args:
            error_fn (Array(Callable)): error functions to use, if empty all available will be used
            kernel (AbstractKernel): Kernel for model
            x_data (Array): X data
            y_data (Array): Y data
        """
        key = random.PRNGKey(seed=seed)

        ## Add custom error fucntions
        for ef in error_fn:
            self._add_error_fn(ef)
        

        ## k-fold crossval
        for i in range(k):
            key, data_key = random.split(key)

            (X_train, Y_train), (X_test, Y_test), _= IFE.utils.train_test_split(
                X=X, Y=Y, f=f, 
                split=(split[0], split[1], 0), 
                key=data_key
            )

            self.model.kernel = self.kernel
            self.model.X = X_train
            self.model.sigma_sq = Y_train.var(axis=0, ddof=1)
            self.model.Y = Y_train
            self.model.frequency = f
            self.model.jitter = model_jitter

            self.model.train(key, num_steps=num_steps, number_restarts=num_restarts)

            y_pred, y_var = self.model.predict(X_test)

            for k in self.error_functions.keys():
                func = self.error_functions[k]["fn"]
                self.error_functions[k]["e"].append(func(Y_test, y_pred))

        self.print_errors()


if __name__ == "__main__":
    from IFE_Surrogate.GP.kernels import Matern12, Matern32
    from IFE_Surrogate.GP.models.wideband_gp import Wideband_GP
    from IFE_Surrogate import plotting
    from numpyro.distributions import Uniform

    dataset = jnp.load(r"C:\Users\aceofspades\ife_surrogate_model\examples\datasets\dataset_7D.npy", allow_pickle=True).item()
    X, Y, f = dataset["X"], dataset["Y"], dataset["f"][:,np.newaxis].T
    d = X.shape[1]

    priors = {
    "lengthscale": Uniform(1e-1, 1e0),
    "power": Uniform(1, 2),
    "noise": Uniform(1e-6, 1e-4),
    "variance": Uniform(1e-3, 1e-2),
    "alpha": Uniform(1e-2, 1e-2),  
    }

    model = Wideband_GP(None, None, None)
    k = Matern32(lengthscale=jnp.ones((d,)), priors=priors)

    cv = Evaluator(model=model, kernel=k, X=X, Y=Y, f=f)
    cv.cross_validate(k=6)


