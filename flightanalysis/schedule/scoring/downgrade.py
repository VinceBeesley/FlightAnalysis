
from flightanalysis.base import Collection
from .criteria import Single, Continuous, Criteria
from .measurement import Measurement
from .results import Results, Result
from typing import Callable
from flightanalysis.state import State 
from geometry import Coord
from dataclasses import dataclass
import numpy as np
import pandas as pd


@dataclass
class DownGrade:
    """This is for Intra scoring, it sits within an El and defines how errors should be measured and the criteria to apply
        measure - a Measurement constructor
        criteria - takes a Measurement and calculates the score
    """
    measure: Callable[[State, State, Coord], Measurement]
    criteria: Criteria

    @property
    def name(self):
        return self.measure.__name__

    
    @staticmethod
    def convolve(data, width):
        kernel = np.ones(width) / width
        return np.convolve(data, kernel, mode='same')
    

    def __call__(self, fl, tp, coord) -> Result:
        measurement = self.measure(fl, tp, coord)

        vals = self.criteria.prepare(measurement.value, measurement.expected)    
    
        if isinstance(self.criteria, Single):
            id, dg = self.criteria([len(vals)-1], [vals[-1]])

        elif isinstance(self.criteria, Continuous):
            if len(vals) > 11:
                vals = self.convolve(vals, 5)
                id, dg = self.criteria(
                    list(range(5,len(vals)-5,1)), 
                    vals[5:-5]
                )
            else:
                id, dg = len(vals)-1, 0.0
        else:
            raise TypeError(f'Expected a Criteria, got {self.criteria.__class__.__name__}')
        
        return Result(self.measure.__name__, measurement, dg, id)


class DownGrades(Collection):
    VType = DownGrade
    uid = "name"

    def apply(self, el, fl, tp, coord) -> Results:
        return Results(el.uid, [dg(fl, tp, coord) for dg in self])
       