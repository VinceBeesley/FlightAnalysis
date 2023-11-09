from __future__ import annotations
import numpy as np
import numpy.typing as npt
from dataclasses import dataclass
from .. import Criteria
from geometry import Point

@dataclass
class Single(Criteria):

    def prepare(self, value: npt.NDArray, expected: float):
        if self.comparison == 'absolute':
            return abs(expected - value)
        elif self.comparison == 'ratio':
            ae = abs(expected)
            af = abs(value)
            return np.maximum(af,ae) / np.minimum(af,ae)
        else:
            raise ValueError('self.comparison must be "absolute" or "ratio"')


    def __call__(self, ids, values):
        vals= np.array(values)
        return ids, vals, self.lookup(vals)
