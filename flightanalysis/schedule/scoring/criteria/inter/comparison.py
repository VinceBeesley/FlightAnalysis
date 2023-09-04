from __future__ import annotations
import numpy as np
import numpy.typing as npt
from .. import Criteria
from dataclasses import dataclass


@dataclass
class Comparison(Criteria):
    def __call__(self, ids: npt.ArrayLike, data: npt.ArrayLike):
        vals = np.concatenate([[data[0]],data])
        if self.comparison == 'absolute':
            errors = np.abs(vals[:-1] - vals[1:])
        elif self.comparison == 'ratio':
            vals = np.abs(vals)
            errors = np.maximum(vals[:-1], vals[1:]) / np.minimum(vals[:-1], vals[1:]) - 1

        return ids, errors, self.lookup(errors)

    