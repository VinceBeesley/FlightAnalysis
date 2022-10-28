
import numpy as np
import pandas as pd
from . import Criteria, Result


class Comparison:
    def __init__(self, criteria: Criteria, initial_value=None):
        self.criteria = criteria
        self.initial_value = initial_value

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
            criteria = self.criteria.to_dict(),
            initial_value = self.initial_value
        )

    @staticmethod
    def from_dict(data:dict):
        return Comparison(
            Criteria.from_dict(data["criteria"]),
            initial_value = data["initial_value"]
        )

    