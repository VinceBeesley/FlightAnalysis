from __future__ import annotations
from dataclasses import dataclass
import numpy as np

@dataclass
class Exponential:
    factor: float
    exponent: float
    limit: float = 10
    def __call__(self, value):
        val = self.factor * value ** self.exponent
        return np.minimum(val, self.limit)
        
    @staticmethod
    def linear(factor: float):
        return Exponential(factor, 1)
    
    @staticmethod
    def fit_points(xs, ys, limit=10, **kwargs):
        from scipy.optimize import curve_fit
        def f(x, factor, exponent):
            return factor * x ** exponent
        res = curve_fit(f, xs, ys)

        return Exponential(res[0][0], res[0][1], limit)

free = Exponential(0,1)
