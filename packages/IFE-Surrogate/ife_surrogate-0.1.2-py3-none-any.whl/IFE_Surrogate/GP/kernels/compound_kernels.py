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
class KernelOperator(AbstractKernel):
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
    #TODO fix this somehow
    def __post_init__(self):
        #priors = {"k1": self.kernel_1.priors, "k2":  self.kernel_2.priors}
        #self.priors = priors
        pass

    def get_priors(self):
        """
        Get the kernel priors.

        Returns:
            A dictionary containing the kernel priors.
        """
        temp1 = self.kernel_1.get_priors()
        temp11 = {"k1__"+k : v for k, v in temp1.items()}

        temp2 = self.kernel_2.get_priors()
        temp22 = {"k2__"+k : v for k, v in temp2.items()}
        return temp11 | temp22

    
    def get_params(self) -> Dict[str, Array]:
        """
        Get the kernel parameters.

        Returns:
            A dictionary containing the kernel parameters.
        """
        temp1 = self.kernel_1.get_params()
        temp11 = {"k1__"+k : v for k, v in temp1.items()}

        temp2 = self.kernel_2.get_params()
        temp22 = {"k2__"+k : v for k, v in temp2.items()}
        return temp11 | temp22


    def sample_hyperparameters(self, key: Key) -> Dict[str, Array]:
        """
        Sample new parameters from the prior distribution.


        Args:
            key: JAX random key.

        Returns: 
            A dictionary containing sampled parameters.
        """
        
        # key1, key2 = jr.split(key, 2)

        params = self.get_params()
        prefixes = set([])
        for p in params.keys():
            prefixes.add(p.rsplit("__", 1)[0] + "__")

        kernels = [self.get_kernel(k) for k in prefixes]

        raw = {prefix : kernel.sample_hyperparameters(key) for prefix, kernel in zip(prefixes, kernels)}
        ret = {}
        for prefix, sample_item in raw.items():
            for name, sample in sample_item.items():
                ret[prefix + name] = sample

        return ret




    def get_kernel(self, path: str):
        if path.startswith("k1__"):
            if isinstance(self.kernel_1, KernelOperator):
                return self.kernel_1.get_kernel(path.split("__", 1)[1])
            else:
                return self.kernel_1
        elif path.startswith("k2__"):
            if isinstance(self.kernel_2, KernelOperator):
                return self.kernel_2.get_kernel(path.split("__", 1)[1])
            else:
                return self.kernel_2
        else:
            print("Warning: Invalid kernel call ", path, "Needs to start with 'k1__' or 'k2__'")
        


    
    def update_params(self, params: Dict) -> None:
        """
        Update the kernel parameters of both kernels.

        Args:
            params: A dictionary containing the new parameters.
        """
        
        for k, v in params.items():
            ksplit = k.split("__", 1)
            if len(ksplit) == 2:
                kernel_nr, param = ksplit
                if kernel_nr == "k1":
                    self.kernel_1.update_params({param: v})
                elif kernel_nr == "k2":
                    self.kernel_2.update_params({param: v})
            else:
                print("??")







        

@struct.dataclass
class ProductKernel(KernelOperator):
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

    def evaluate(self, x1: Array, x2: Array) -> Array:
        return_1 = self.kernel_1(x1, x2)
        return_2 = self.kernel_2(x1, x2)
        return return_1 * return_2
    



@struct.dataclass
class SumKernel(KernelOperator):
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

    def evaluate(self, x1: Array, x2: Array) -> Array:
        return_1 = self.kernel_1(x1, x2)
        return_2 = self.kernel_2(x1, x2)
        return return_1 + return_2
    

    from flax import struct
import jax.numpy as jnp
from typing import Dict
from jaxtyping import Array, Key
from IFE_Surrogate.GP.kernels.base_kernel import AbstractKernel

@struct.dataclass
class SeparableKernel(KernelOperator):
    """
    A separable kernel that factors into a product of a kernel over x
    and a kernel over w:

    .. math::

        k((x, w), (x', w')) = k_x(x, x') \cdot k_w(w, w')

    Attributes:
        kx: Kernel acting on the x inputs.
        kw: Kernel acting on the w inputs.
    """
    #kx: AbstractKernel = struct.field(pytree_node=False)
    #kw: AbstractKernel = struct.field(pytree_node=False)


    def evaluate(self, inputs1, inputs2):
        """
        inputs1: tuple (X, W)
        inputs2: tuple (X, W)
        X: shape (N_x, D_x)
        W: shape (N_w, D_w)
        """
        X1, W1 = inputs1
        X2, W2 = inputs2
        Kx = self.kernel_1(X1, X2)
        Kw = self.kernel_2(W1, W2)
        return Kx, Kw 
    
    # def evaluate(self, x, w, x2, w2):
    #     return self.kernel_1(x, x2), self.kernel_2(w, w2)

    # def get_priors(self):
    #     px = {"kx__" + k: v for k, v in self.kx.get_priors().items()}
    #     pw = {"kw__" + k: v for k, v in self.kw.get_priors().items()}
    #     return px | pw

    # def get_params(self) -> Dict[str, Array]:
    #     px = {"kx__" + k: v for k, v in self.kx.get_params().items()}
    #     pw = {"kw__" + k: v for k, v in self.kw.get_params().items()}
    #     return px | pw

    # def sample_hyperparameters(self, key: Key) -> Dict[str, Array]:
    #     import jax.random as jr
    #     key_x, key_w = jr.split(key)
    #     px = {"kx__" + k: v for k, v in self.kx.sample_hyperparameters(key_x).items()}
    #     pw = {"kw__" + k: v for k, v in self.kw.sample_hyperparameters(key_w).items()}
    #     return px | pw

    # def update_params(self, params: Dict[str, Array]) -> None:
    #     px = {k.split("__", 1)[1]: v for k, v in params.items() if k.startswith("kx__")}
    #     pw = {k.split("__", 1)[1]: v for k, v in params.items() if k.startswith("kw__")}
    #     if px:
    #         self.kx.update_params(px)
    #     if pw:
    #         self.kw.update_params(pw)
