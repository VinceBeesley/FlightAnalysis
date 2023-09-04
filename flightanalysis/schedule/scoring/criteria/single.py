from __future__ import annotations
from . import Criteria
from flightanalysis.schedule.scoring import Result, Results, Measurement
from dataclasses import dataclass
import numpy as np
import numpy.typing as npt

@dataclass
class Single(Criteria):

    def __call__(self, ids: npt.ArrayLike, value: npt.ArrayLike):
        """get a Result object for a set of errors."""
        return ids, self.lookup(np.abs(value))
    

