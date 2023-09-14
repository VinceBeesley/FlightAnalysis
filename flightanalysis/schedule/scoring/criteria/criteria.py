import numpy as np
from .exponential import Exponential, free
from dataclasses import dataclass, field

@dataclass
class Criteria:
    lookup: Exponential = field(default_factory=lambda : free)
    comparison: str='absolute'



    def to_dict(self):
        data = self.__dict__.copy()
        lookup = data.pop('lookup')
        return dict(
            kind=self.__class__.__name__,
            lookup=lookup.__dict__,
            **data
        )
    
    @staticmethod
    def from_dict(data: dict):
        data = data.copy()
        name = data.pop('kind')
        for Crit in Criteria.__subclasses__():
            if Crit.__name__ == name:
                lookup = data.pop('lookup')
                return Crit(lookup=Exponential(**lookup), **data)
        raise ValueError(f'cannot parse Criteria from {data}')
    
    def to_py(self):
        return f"{self.__class__.__name__}(Exponential({self.lookup.factor},{self.lookup.exponent}, {self.lookup.limit}), '{self.comparison}')"