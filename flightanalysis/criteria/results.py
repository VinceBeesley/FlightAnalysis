import numpy as np
import pandas as pd
from flightanalysis.base.collection import Collection



class Result:
    def __init__(self, name: str, errors: np.ndarray, downgrades: np.ndarray):
        self.name = name
        self.errors = errors
        self.downgrades = downgrades
        self.value = sum(self.downgrades)
        self.downgrade = np.trunc(self.value * 2) / 2


class Results(Collection):
    VType = Result
    uid="name"
    def downgrade(self):
        return sum([cr.downgrade for cr in self])

    def downgrade_summary(self):
        return {r.name: r.downgrades for r in self}