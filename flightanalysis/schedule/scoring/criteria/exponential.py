from __future__ import annotations
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


free = Exponential(0,1)
