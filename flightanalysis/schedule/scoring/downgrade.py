
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
            id, error, dg = self.criteria([len(vals)-1], [vals[-1]])
            dg = dg * measurement.visibility[id]
        elif isinstance(self.criteria, Continuous):
            if len(vals) > 11:
                tempvals = self.convolve(vals, 5)[5:-5]
                id, error, dg = self.criteria(
                    list(range(5,len(fl)-5,1)), 
                    tempvals
                )
                vals = np.full(len(fl), np.nan)
                vals[5:-5] = tempvals
                
                #take the average visibility for the given downgrade
                rids = np.concatenate([[0], id])
                vis = np.array([np.mean(measurement.visibility[a:b]) for a, b in zip(rids[:-1], rids[1:])])
                dg = vis * dg
            else:
                id, error, dg = [len(vals)-1], [0.0], [0.0]
        else:
            raise TypeError(f'Expected a Criteria, got {self.criteria.__class__.__name__}')
        
        return Result(self.measure.__name__, measurement, vals, error, dg, id)


class DownGrades(Collection):
    VType = DownGrade
    uid = "name"

    def apply(self, el, fl, tp, coord) -> Results:
        return Results(el.uid, [dg(fl, tp, coord) for dg in self])
       