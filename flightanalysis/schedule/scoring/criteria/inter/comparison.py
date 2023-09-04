from __future__ import annotations
import numpy as np
import numpy.typing as npt
from .. import Criteria
from dataclasses import dataclass


@dataclass
class Comparison(Criteria):
    def __call__(self, ids: npt.ArrayLike, data: npt.ArrayLike):

        a = data[0]
        res = []
        for i, id in enumerate(ids):
            if self.comparison == 'absolute':
                res.append(self.lookup(abs(a - data[i])))
            elif self.comparison == 'ratio':
                res.append(self.lookup(max(a, data[i]) / min(a, data[i]) - 1))
            a = data[i]

        return ids, res

    