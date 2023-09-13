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
        from scipy.optimize import differential_evolution
        def f(x):
            return sum(abs(ys - Exponential(x[0],x[1])(xs)))
        res = differential_evolution(f, ((0,100),(0,5)), **kwargs)
        return Exponential(res.x[0], res.x[1], limit)


free = Exponential(0,1)
