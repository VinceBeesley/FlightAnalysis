
from flightanalysis.base import Collection
from .criteria import Criteria
from .measurement import Measurement
from .results import Results, Result
from typing import Callable
from flightanalysis.state import State 
from geometry import Coord
from dataclasses import dataclass


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

    def __call__(self, el, fl, tp, coord) -> Result:
        if self.criteria.__class__ is Criteria:
            meas = self.measure(fl, tp, coord).exit_only()
        else:
            meas = self.measure(fl, tp, coord)

        return Result(
            self.measure.__name__,
            meas,
            self.criteria(meas)
        )

#    def __repr__(self):
#        return f"Downgrade({self.name}, {self.criteria.__class__.__name__})"


class DownGrades(Collection):
    VType = DownGrade
    uid = "name"

    def apply(self, el, fl, tp, coord) -> Results:
        return Results(el.uid, [dg(el, fl, tp, coord) for dg in self])
       