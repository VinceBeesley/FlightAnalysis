from __future__ import annotations
import inspect
from typing import Callable
import numpy as np
from flightanalysis.schedule.scoring.measurement import Measurement

free = lambda x: np.zeros_like(x)


class Criteria:
    def __init__(self, lookup:Callable=free, errortype:str="ratio", slu=None):
        """
        Args:
            lookup (Callable): a function that returns a score for an error
            slu (string): a string representation of the function
            errortype (str): either "ratio" or "absolute"
        """
        self.lookup = lookup
        self.errortype = errortype
        self.slu=slu if slu else inspect.getsourcelines(self.lookup)[0][0].split("=")[1].strip()

    def preprocess(self, flown, expected):
        if self.errortype == "ratio":
            af = abs(flown)
            ae = abs(expected)
            return np.maximum(af, ae) / np.minimum(af, ae) - 1
        elif self.errortype == "absolute":
            return abs(flown - expected)

    def __call__(self, m: Measurement):
        return self.lookup(self.preprocess(m.value, m.expected)) * m.visibility

    def to_dict(self) -> dict[str, str]:
        return dict(
            kind = self.__class__.__name__,
            errortype = self.errortype,
            slu = self.slu
        )

    @classmethod
    def from_dict(Cls, data) -> Criteria:
        data=data.copy()
        criteria = {c.__name__: c for c in Cls.__subclasses__()}
        criteria[Cls.__name__] = Cls
        Child = criteria[data.pop('kind')]
        func = eval(data["slu"])
        return Child(lookup=func,**data)
