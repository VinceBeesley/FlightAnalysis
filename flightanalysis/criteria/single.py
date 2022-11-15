import numpy as np
import pandas as pd
from typing import List, Dict, Callable
from .results import Result, Results
import inspect


class Single:
    """This class creates a function to return a result for a set of errors. 
    """
    def __init__(self, lookup: Callable, preprocess: Callable=None):
        """
        Args:
            lookup (Callable): a function that returns a score for a given error
            preprocess (Callable, optional): A function to apply to the input value to return the error.
        """
        self.lookup = lookup        
        if preprocess is None:
            self.preprocess = lambda x: x
        else:
            self.preprocess = preprocess
    
    def __call__(self, name: str, data: np.ndarray, pp = True) -> List[float]:
        """get a Result object for a set of errors."""
        pdata = self.preprocess(data) if pp else data
        return Result(name,data,self.lookup(pdata))

    def to_dict(self):
        return dict(
            kind = self.__class__.__name__,
            lookup = inspect.getsourcelines(self.criteria)[0][0].split("=")[1].strip(),
            preprocess = inspect.getsourcelines(self.criteria)[0][0].split("=")[1].strip()
        )

    @staticmethod
    def from_dict(data:dict):
        return Single(eval(data["lookup"]),eval(data["preprocess"]))