
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

from scipy.signal import butter, filtfilt


def butter_filter(data, cutoff):
    return filtfilt(*butter(2, cutoff / 15, btype='low', analog=False), data)


@dataclass
class DownGrade:
    """This is for Intra scoring, it sits within an El and defines how errors should be measured and the criteria to apply
        measure - a Measurement constructor
        criteria - takes a Measurement and calculates the score
    """
    measure: Callable[[State, State, Coord], Measurement]
    criteria: Criteria

    def to_dict(self):
        return dict(
            measure=self.measure.__name__,
            criteria=self.criteria.to_dict()
        )

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
            if len(measurement) < 18:
                #for now, if an element lasts less than 0.5 seconds then we assume it is perfect
                return Result(self.measure.__name__, measurement, [0], [0], [0], [0])

            endcut = 4 #min(3, int((len(vals) - 5) / 2))
            
            tempvals = butter_filter(vals[endcut:-endcut], 1)
       
            # for absolute errors you keep getting downgraded for the same error as it becomes more visible.
            # this is because there is a correct reference value the pilot should be aiming for
            # roll angle, track, 
            if self.criteria.comparison == 'absolute':
                tempvals = tempvals[0] + np.cumsum(np.gradient(tempvals) * measurement.visibility[endcut:-endcut])  
       
            id, error, dg = self.criteria(
                list(range(endcut,len(fl)-endcut)), 
                tempvals
            )
            vals = np.full(len(fl), np.nan)
            vals[endcut:-endcut] = tempvals
            
            if self.criteria.comparison == 'ratio':
                #for ratio errors visiblity factors are applied to the downgrades, so if the initial
                #error happened when it was hard to see then you don't get downgraded further as
                #it becomes more apparant. This is because the reference is set by the pilot
                #rollrate, speed, radius,  
                rids = np.concatenate([[0], id])
                vis = np.array([np.mean(measurement.visibility[a:b]) for a, b in zip(rids[:-1], rids[1:])])
                dg = vis * dg
        else:
            raise TypeError(f'Expected a Criteria, got {self.criteria.__class__.__name__}')
        
        return Result(self.measure.__name__, measurement, vals, error, dg, id)


class DownGrades(Collection):
    VType = DownGrade
    uid = "name"

    def apply(self, el, fl, tp, coord) -> Results:
        return Results(el.uid, [dg(fl, tp, coord) for dg in self])
       