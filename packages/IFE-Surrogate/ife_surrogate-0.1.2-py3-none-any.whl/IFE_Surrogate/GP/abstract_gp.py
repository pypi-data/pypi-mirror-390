# ------------------------------------------------------------------------------
# Project: IFE_Surrogate
# Authors: Tobias Leitgeb, Julian Tischler
# CD Lab 2025
# ------------------------------------------------------------------------------
from jaxtyping import Array
from abc import ABC, abstractmethod
import typing
from IFE_Surrogate.GP.kernels.base_kernel import AbstractKernel
import h5py
import numpy as np

Kernel = typing.TypeVar("Kernel", bound=AbstractKernel)

## move to IFE_Surrogate folder

## Rename to SurrogateModel -> NeuralNet also use this as skeleton
class AbstractGP(ABC):
    """ 
        Abstract base class of a GP, to be used as skeleton for actual GP implementations.
    """
    ## TODO 
    ## get rid of kernel, x, and y, convert to keywordargs
    ## conditional constructor; if x, y, kernel is present -> create from x, y, kernel
    ##                          if hdf5 is present -> load from hdf5
    ## (should be loadable from hdf, for example to save an entire surrogates weights)
    def __init__(self, kernel: Kernel, X: Array, Y: Array, hdf5: bool = None):
        if hdf5 is not None:
            self.X = hdf5.get_training_data()
        self.kernel = kernel
        self.X = X
        self.Y = Y

        ## TODO
        ## kernel, x, y should be saved to self._data to be easier to save to hdf5
        ## setter + getter 
        # self._data = {}
        ## dictionary with all the logs
        # self._logs = {}
        ## dictionary with all the predictions
        # self._predictions = {}

    ## Must be implemented in actual model implementation, every SurrogateModel should have a train method
    # @abstractmethod
    # def train():
    #     return
    
    ## Must be implemented in actual model implementation, every SurrogateModel should have a predict method
    @abstractmethod
    def predict():
        return

    def get_attributes(self):
        return self.__dict__

    def save(path="output.h5"):
        pass