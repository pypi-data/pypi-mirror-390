# ------------------------------------------------------------------------------
# Project: IFE_Surrogate
# Authors: Tobias Leitgeb, Julian Tischler
# CD Lab 2025
# ------------------------------------------------------------------------------
from dataclasses import dataclass
from jaxtyping import Array, Key
from typing import Callable, Dict, List
import jax.numpy as jnp
import jax.random as jr
from flax import struct
from IFE_Surrogate.GP.kernels.base_kernel import AbstractKernel


#should maybe change it to this
# from flax import struct

# @struct.dataclass
# class Params:
#     """Holds parameters"""
#     kernel_params: Dict[str, Array]

#TODO
"""
There are problems with the naming scheme when u stack sum kernel and product kernel.
"""
@struct.dataclass
class SumKernel(AbstractKernel):
    r"""
    Represents a kernel that multiplies the outputs of two given kernels:
    
    .. math::

        k(x, x'|\theta_1, \theta_2) = k_1(x, x'|\theta_1) + k_2(x, x'|\theta_2)


    Attributes:
        kernel_1 (AbstractKernel): The first kernel.
        kernel_2 (AbstractKernel): The second kernel.
    """
    kernel_1: AbstractKernel = struct.field(pytree_node=False)
    kernel_2: AbstractKernel = struct.field(pytree_node=False)
    #priors: Dict[str, Callable] = struct.field(pytree_node=False)

    def __post_init__(self):
        priors = {}

        if hasattr(self.kernel_1, "priors") and self.kernel_1.priors is not None:
            for name, prior in self.kernel_1.priors.items():
                if name in self.kernel_1.get_params().keys():
                    priors[f"{name}1"] = prior

        if hasattr(self.kernel_2, "priors") and self.kernel_2.priors is not None:
            for name, prior in self.kernel_2.priors.items():
                if name in self.kernel_2.get_params().keys():
                    priors[f"{name}2"] = prior

        object.__setattr__(self, "priors", priors)

    def evaluate(self, x1: Array, x2: Array) -> Array:
        return_1 = self.kernel_1(x1, x2)
        return_2 = self.kernel_2(x1, x2)
        return return_1 + return_2
    
    def get_params(self) -> Dict[str, Array]:
        """
        Get the kernel parameters.
        Kernel 1 parameters have suffix '1'
        Kernel 2 parameters have suffix '2'

        Returns:
            A dictionary containing the kernel parameters.
        """
        ret_dict = {}
        for k, v in self.kernel_1.__dict__.items():
            if k == "priors":
                continue
            ret_dict[k+"1"] = v
        
        for k, v in self.kernel_2.__dict__.items():
            if k == "priors":
                continue
            ret_dict[k+"2"] = v

        return ret_dict
    

    def sample_hyperparameters(self, key: Key) -> Dict[str, Array]:
        """
        Sample new parameters from the prior distribution.
        Kernel 1 parameters have suffix '1'
        Kernel 2 parameters have suffix '2'

        Args:
            key: JAX random key.

        Returns: 
            A dictionary containing sampled parameters.
        """
        #maybe rewrite this to be more readab
        
        key1, key2 = jr.split(key, 2)
        if self.kernel_1.priors is None:
            print("No priors specified for kernel 1. Returning current parameters.")
            return self.get_params()
        elif self.kernel_2.priors is None:
            print("No priors specified for kernel 2. Returning current parameters.")
            return self.get_params()

        ret_dict = {}
        for param_name_kernel_1, params_kernel_1 in self.kernel_1.__dict__.items():
            if param_name_kernel_1 == "priors":
                continue
            ret_dict[param_name_kernel_1+"1"] = self.kernel_1.priors[param_name_kernel_1].sample(key1, params_kernel_1.shape)

        for param_name_kernel_2, params_kernel_2 in self.kernel_2.__dict__.items():
            if param_name_kernel_2 == "priors":
                continue
            ret_dict[param_name_kernel_2+"2"] = self.kernel_2.priors[param_name_kernel_2].sample(key2, params_kernel_2.shape)
        
        return ret_dict
    
    def update_params(self, params: Dict[str, Array]) -> None:
        """
        Update the kernel parameters of both kernels.

        Args:
            params: A dictionary containing the new parameters.
        """

        for param_name, param in params.items():
            if param_name.endswith("1"):
                self.kernel_1.__dict__[param_name[:-1]] = param
            elif param_name.endswith("2"):
                self.kernel_2.__dict__[param_name[:-1]] = param



@struct.dataclass
class ProductKernel(AbstractKernel):
    r"""
    Represents a kernel that multiplies the outputs of two given kernels:

    .. math::   

        k(x, x'|\theta_1, \theta_2) = k_1(x, x'|\theta_1) + k_2(x, x'|\theta_2)


    Attributes:
        kernel_1 (AbstractKernel): The first kernel.
        kernel_2 (AbstractKernel): The second kernel.
    """
    kernel_1: AbstractKernel = struct.field(pytree_node=False)
    kernel_2: AbstractKernel = struct.field(pytree_node=False)
    #priors: Dict[str, Callable] = struct.field(pytree_node=False)

    def __post_init__(self):
        priors = {}

        if hasattr(self.kernel_1, "priors") and self.kernel_1.priors is not None:
            for name, prior in self.kernel_1.priors.items():
                if name in self.kernel_1.get_params().keys():
                    priors[f"{name}1"] = prior

        if hasattr(self.kernel_2, "priors") and self.kernel_2.priors is not None:
            for name, prior in self.kernel_2.priors.items():
                if name in self.kernel_2.get_params().keys():
                    priors[f"{name}2"] = prior

        object.__setattr__(self, "priors", priors)


    def evaluate(self, x1: Array, x2: Array) -> Array:
        """
        Evaluate the product of the two kernels on the input data.

        Args:
            x1 (Array): First input array.
            x2 (Array): Second input array.

        Returns:
            Array: The product of the two kernel evaluations.
        """
        return self.kernel_1(x1, x2) * self.kernel_2(x1, x2)

    def get_params(self) -> Dict[str, Array]:
        """
        Retrieve the parameters of both kernels.

        The parameters of `kernel_1` are suffixed with '1', and the parameters of `kernel_2` are suffixed with '2'.

        Returns:
            Dict[str, Array]: A dictionary containing kernel parameters.
        """
        params = {
            f"{k}1": v for k, v in self.kernel_1.__dict__.items() if k != "priors"
        }
        params.update({
            f"{k}2": v for k, v in self.kernel_2.__dict__.items() if k != "priors"
        })
        return params

    def sample_hyperparameters(self, key: Array) -> Dict[str, Array]:
        """
        Sample new hyperparameters from the prior distribution.

        Args:
            key (Array): JAX random key of shape (2,).

        Returns:
            Dict[str, Array]: A dictionary containing sampled parameters.
        Returns: 
            A dictionary containing sampled parameters.
        """
        
        key1, key2 = jr.split(key, 2)

        # Return current parameters if priors are not specified
        if self.kernel_1.priors is None or self.kernel_2.priors is None:
            print("No priors specified for one or both kernels. Returning current parameters.")
        #maybe rewrite this to be more readable
        #assert isinstance(key, Key), "key must be a jax random key"

        key1, key2 = jr.split(key, 2)
        if self.kernel_1.priors is None:
            print("No priors specified for kernel 1. Returning current parameters.")
            return self.get_params()
        elif self.kernel_2.priors is None:
            print("No priors specified for kernel 2. Returning current parameters.")
            return self.get_params()

        sampled_params = {}
        
        for name, value in self.kernel_1.__dict__.items():
            if name != "priors":
                sampled_params[f"{name}1"] = self.kernel_1.priors[name].sample(key1, value.shape)
        
        for name, value in self.kernel_2.__dict__.items():
            if name != "priors":
                sampled_params[f"{name}2"] = self.kernel_2.priors[name].sample(key2, value.shape)
        ret_dict = {}
        for param_name_kernel_1, params_kernel_1 in self.kernel_1.__dict__.items():
            if param_name_kernel_1 == "priors":
                continue
            ret_dict[param_name_kernel_1+"1"] = self.kernel_1.priors[param_name_kernel_1].sample(key1, params_kernel_1.shape)

        for param_name_kernel_2, params_kernel_2 in self.kernel_2.__dict__.items():
            if param_name_kernel_2 == "priors":
                continue
            ret_dict[param_name_kernel_2+"2"] = self.kernel_2.priors[param_name_kernel_2].sample(key2, params_kernel_2.shape)
        
        return sampled_params
    
    def update_params(self, params: Dict[str, Array]):
        """
        Update the parameters of both kernels.

        Args:
            params (Dict[str, Array]): A dictionary containing new parameter values.
        """

        for param_name, param in params.items():
            if param_name.endswith("1"):
                self.kernel_1.__dict__[param_name[:-1]] = param
            elif param_name.endswith("2"):
                self.kernel_2.__dict__[param_name[:-1]] = param


@struct.dataclass
class SeparableKernel(AbstractKernel):
    """
    k_joint((x,w), (x',w')) = k_x(x,x') * k_w(w,w')
    """
    kernel_x: AbstractKernel = struct.field(pytree_node=False)
    kernel_w: AbstractKernel = struct.field(pytree_node=False)
    dim_x: int = struct.field(pytree_node=False)  # number of x dims

    def evaluate(self, X1: Array, X2: Array) -> Array:
        x1, w1 = X1[:, :self.dim_x], X1[:, self.dim_x:]
        x2, w2 = X2[:, :self.dim_x], X2[:, self.dim_x:]

        Kx = self.kernel_x(x1, x2)
        Kw = self.kernel_w(w1, w2)
        return Kx * Kw

    def get_priors(self):
        temp1 = {"kx__" + k: v for k, v in self.kernel_x.get_priors().items()}
        temp2 = {"kw__" + k: v for k, v in self.kernel_w.get_priors().items()}
        return temp1 | temp2

    def get_params(self):
        temp1 = {"kx__" + k: v for k, v in self.kernel_x.get_params().items()}
        temp2 = {"kw__" + k: v for k, v in self.kernel_w.get_params().items()}
        return temp1 | temp2

    def update_params(self, params: Dict[str, Array]) -> None:
        kx_params = {k.split("__", 1)[1]: v for k, v in params.items() if k.startswith("kx__")}
        kw_params = {k.split("__", 1)[1]: v for k, v in params.items() if k.startswith("kw__")}
        self.kernel_x.update_params(kx_params)
        self.kernel_w.update_params(kw_params)
