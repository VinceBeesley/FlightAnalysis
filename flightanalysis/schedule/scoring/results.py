from __future__ import annotations
import numpy as np
import pandas as pd
from flightanalysis.base.collection import Collection
from flightanalysis.schedule.scoring.measurement import Measurement


class Result:
    def __init__(self, name: str,  measurement: Measurement, dgs: np.ndarray):
        self.name = name
        self.measurement = measurement
        self.dgs = dgs
        self.value = sum(self.dgs)


class Results(Collection):
    VType = Result
    uid="name"
    def downgrade(self):
        return sum([cr.value for cr in self])

    def downgrade_summary(self):
        return {r.name: r.dgs for r in self if len(r.dgs > 0)}

    def downgrade_df(self) -> pd.DataFrame:
        dgs = self.downgrade_summary()
        if len(dgs) == 0:
            return pd.DataFrame()
        max_len = max([len(v) for v in dgs.values()])
        extend = lambda vals: [vals[i] if i < len(vals) else 0.0 for i in range(max_len)]
        return pd.DataFrame.from_dict({k:extend(v) for k,v in dgs.items()})


