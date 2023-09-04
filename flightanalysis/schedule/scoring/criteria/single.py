from __future__ import annotations
from . import Criteria
from flightanalysis.schedule.scoring import Result, Results, Measurement
from dataclasses import dataclass
import numpy as np
import numpy.typing as npt
from geometry import Point

@dataclass
class Single(Criteria):

    def prepare(self, value: Point, expected: Point):
        if self.comparison == 'absolute':
            return abs(expected) - abs(value)
        elif self.comparison == 'ratio':
            ae = abs(expected)
            af = abs(value)
            return np.maximum(af,ae) / np.minimum(af,ae)
        else:
            raise ValueError('self.comparison must be "absolute" or "ratio"')

    def __call__(self, ids: npt.ArrayLike, value: npt.ArrayLike):
        """get a Result object for a set of errors."""
        return ids, np.abs(value), self.lookup(np.abs(value))
    

