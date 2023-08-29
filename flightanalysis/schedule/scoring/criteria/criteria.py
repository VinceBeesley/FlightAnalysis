from __future__ import annotations
import inspect
from typing import Callable, List
import numpy as np
from flightanalysis.schedule.scoring.measurement import Measurement
from dataclasses import dataclass


@dataclass
class Exponential:
    factor: float
    exponent: float
    def __call__(self, value):
        return self.factor * value ** self.exponent
    
    @staticmethod
    def linear(factor: float):
        return Exponential(factor, 1)
    
    @staticmethod
    def fit_points(xs, ys, **kwargs):
        from scipy.optimize import differential_evolution
        def f(x):
            return sum(abs(ys - Exponential(x[0],x[1])(xs)))
        res = differential_evolution(f, ((0,100),(0,5)), **kwargs)
        return Exponential(res.x[0], res.x[1])


    def __str__(self):
        return f'Exponential({self.factor:.2f}, {self.exponent:.2f})'
    
free = Exponential(0,1)#lambda x: np.zeros_like(x)



class Criteria:
    def __init__(self, lookup:Exponential=free, errortype:str="ratio"):
        """
        Args:
            lookup (Callable): a function that returns a score for an error
            slu (string): a string representation of the function
            errortype (str): either "ratio" or "absolute"
        """
        self.lookup = lookup
        self.errortype = errortype

    def pp_ratio(self, flown, expected):
        af = abs(flown)
        ae = abs(expected)
        return np.maximum(af, ae) / np.minimum(af, ae) - 1

    def pp_absolute(self, flown, expected):
        return abs(flown - expected)
    
    def preprocess(self, flown, expected):
        if self.errortype == "ratio":
            af = abs(flown)
            ae = abs(expected)
            return np.maximum(af, ae) / np.minimum(af, ae) - 1
        elif self.errortype == "absolute":
            return abs(flown - expected)

    def __call__(self, m: Measurement):
        return self.lookup(self.preprocess(m.value, m.expected)) * m.visibility

    def __str__(self):
        return f'Criteria({self.lookup}, {self.errortype})'

    def to_dict(self) -> dict[str, str]:
        return dict(
            kind = self.__class__.__name__,
            errortype = self.errortype,
            lookup=self.lookup.__dict__
        )

    @classmethod
    def from_dict(Cls, data) -> Criteria:
        data=data.copy()
        criteria = {c.__name__: c for c in Cls.__subclasses__()}
        criteria[Cls.__name__] = Cls
        Child = criteria[data.pop('kind')]
        func = Exponential(**data.pop('lookup'))
        return Child(lookup=func,**data)
