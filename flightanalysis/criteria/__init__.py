from __future__ import annotations
import numpy as np
import pandas as pd
from pandas.api.types import is_list_like
from .results import Result, Results
from flightanalysis.base.collection import Collection


class Criteria:
    pass

    @classmethod
    def from_dict(Cls, data):
        for Child in Cls.__subclasses__():
            if Child.__name__ == data["kind"]:
                return Child.from_dict(data)
        raise ValueError("unknown criteria")


f3a_radius = lambda x : (1 - 1/(x+1)) * 4
f3a_length = lambda x : (1 - 1/(x+1)) * 4
f3a_angle = lambda x: x/15
f3a_speed = lambda x : (1 - 1/(x+1))
f3a_roll_rate = lambda x : (1 - 1/(x+1))
imac_angle = lambda x: x/10
hard_zero = lambda x: 0 if x==0 else 10
free = lambda x: 0 if not is_list_like(x) else np.zeros(len(x))


from .single import Single
from .continuous import Continuous
from .comparison import Comparison
from .combination import Combination

basic_angle_f3a = Single(f3a_angle, lambda x : np.abs(np.degrees(x) % (2 * np.pi)))

intra_f3a_angle = Continuous(f3a_angle, lambda x: np.degrees(x))
intra_f3a_radius = Continuous(f3a_radius, lambda x: (x / x[0] - 1) )
intra_f3a_speed = Continuous(f3a_speed, lambda x: (x / x[0] - 1) )
intra_f3a_roll_rate = Continuous(f3a_roll_rate, lambda x: np.degrees(x))

inter_f3a_radius = Comparison(f3a_radius, None)
inter_f3a_speed = Comparison(f3a_speed, None)
inter_f3a_length = Comparison(f3a_length, None)
inter_f3a_roll_rate = Comparison(f3a_roll_rate, None)
inter_free = Comparison(free, None)


class DownGrade:
    def __init__(self, name, measurement, criteria: Criteria):
        self.name = name
        self.measurement = measurement
        self.criteria = criteria

    def measure(self, el, flown, template):
        return self.criteria.preprocess(getattr(el, self.measurement)(flown, template))
    
    def apply(self, el, flown, template):
        return self.criteria(self.name, self.measure(el, flown, template), False)


class DownGrades(Collection):
    VType = DownGrade
    uid = "name"

    def apply(self, el, fl, tp):
        return Results([es.criteria(es.name, es.measure(el, fl, tp), False) for es in self])
       