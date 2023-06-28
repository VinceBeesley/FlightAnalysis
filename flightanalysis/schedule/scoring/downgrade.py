
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

    def measure_element(self, fl, tp, coord) -> Measurement:
        return self.measure(fl, tp, coord)
    
    def apply(self, measurement: Measurement):
        return self.criteria(self.name, measurement, False)
    
    def __call__(self, el, fl, tp, coord) -> Result:
        measurement = self.measure_element(fl, tp, coord)
        return Result(
            f"{el.uid}_{self.measure.__name__}",
            measurement,
            self.criteria(measurement)
        )


class DownGrades(Collection):
    VType = DownGrade
    uid = "name"

    def apply(self, el, fl, tp, coord) -> Results:
        return Results([dg(el, fl, tp, coord) for dg in self])
       