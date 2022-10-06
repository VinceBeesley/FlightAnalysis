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
        return {r.name: r.downgrades for r in self if len(r.downgrades > 0)}

    def downgrade_df(self):
        dgs = self.downgrade_summary()
        if len(dgs) == 0:
            return pd.DataFrame()
        max_len = max([len(v) for v in dgs.values()])
        extend = lambda vals: [vals[i] if i < len(vals) else 0.0 for i in range(max_len)]
        return pd.DataFrame.from_dict({k:extend(v) for k,v in dgs.items()})


