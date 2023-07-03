
from flightanalysis.base import Collection
from .criteria import Criteria
from .measurement import Measurement
from .results import Results, Result
from typing import Callable
from flightanalysis.state import State 
from geometry import Coord


class DownGrade:
    def __init__(
            self, 
            measure: Callable[[State, State, Coord], Measurement], 
            criteria: Criteria
        ):
        self.measure = measure
        self.criteria = criteria

    @property
    def name(self):
        return self.measure.__name__

    def __call__(self, el, fl, tp, coord) -> Result:
        if self.criteria.__class__ is Criteria:
            meas = self.measure(fl[-1], tp[-1], coord)
        else:
            meas = self.measure(fl, tp, coord)

        return Result(
            self.measure.__name__,
            meas,
            self.criteria(meas)
        )

    def __repr__(self):
        return f"Downgrade({self.name}, {self.criteria.__class__.__name__})"

class DownGrades(Collection):
    VType = DownGrade
    uid = "name"

    def apply(self, el, fl, tp, coord) -> Results:
        return Results([dg(el, fl, tp, coord) for dg in self])
       