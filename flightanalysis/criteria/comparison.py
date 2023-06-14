
import numpy as np
import pandas as pd
from . import Result
from typing import Callable
import inspect

class Comparison:
    def __init__(self, criteria: Callable, initial_value=None, scr: str=None):
        self.criteria = criteria
        self.initial_value = initial_value
        self.scr = scr if scr else inspect.getsourcelines(self.criteria)[0][0].split("=")[1].strip()

    def lookup(self,value):
        try:
            return self.criteria(value)
        except IndexError:
            raise ValueError(f"The requested ratio of {value} is not present in levels {self.levels}")
            
            
    def __call__(self, name, data):
        if len(data) == 0:
            return Result(name, np.array([]), np.array([]))
        cval = data[0] if self.initial_value is None else self.initial_value
        data = np.concatenate([np.array([cval]), data])
        ratios = data[1:] / data[:-1] - 1
        return Result(
            name, 
            ratios,
            self.lookup(np.abs(ratios))
        )

    def to_dict(self):
        return dict(
            kind = self.__class__.__name__,
            criteria = self.scr,
            initial_value = self.initial_value
        )

    @staticmethod
    def from_dict(data:dict):
        return Comparison(
            eval(data["criteria"]),
            initial_value = data["initial_value"],
            scr=data["criteria"]
        )

    