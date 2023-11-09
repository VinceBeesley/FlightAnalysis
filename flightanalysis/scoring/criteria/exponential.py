from __future__ import annotations
from dataclasses import dataclass, field
import numpy as np

@dataclass
class Exponential:
    factor: float
    exponent: float
    limit: float = field(default=10)
    def __call__(self, value):
        val = self.factor * value ** self.exponent
        return np.minimum(val, self.limit)
        
    @staticmethod
    def linear(factor: float):
        return Exponential(factor, 1)
    
    @staticmethod
    def fit_points(xs, ys, limit=10):
        from scipy.optimize import curve_fit
        res = curve_fit(
            lambda x, factor, exponent: factor * x ** exponent,
            xs, 
            ys)

        return Exponential(res[0][0], res[0][1], limit)

free = Exponential(0,1)
