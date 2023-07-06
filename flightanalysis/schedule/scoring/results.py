from __future__ import annotations
from typing import Any, Dict, List, Union
import numpy as np
import pandas as pd
from flightanalysis.base import Collection, Table

from flightanalysis.schedule.scoring.measurement import Measurement
from dataclasses import dataclass

@dataclass
class Result:
    """
    Intra - this Result covers the downgrades applicable to things like the change of radius within an element.
    Inter - This result covers the downgrades applicable to a set of loop diameters within a manoevre (one ManParm)
    """
    name: str
    measurement: Measurement
    dgs: np.ndarray
    keys: str=None

    @property
    def value(self):
        return sum(self.dgs)


class Results(Collection):
    """
    Intra - the Results collection covers all the downgrades in one element
    Inter - the Results collection covers all the downgrades in one Manoeuvre
    """
    VType = Result
    uid="name"

    def __init__(self, name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name

    def downgrade(self):
        return sum([cr.value for cr in self])

    def downgrade_summary(self):
        return {r.name: r.dgs for r in self if len(r.dgs > 0)}

    def downgrade_df(self) -> pd.DataFrame:
        dgs = self.downgrade_summary()
        if len(dgs) == 0:
            return pd.DataFrame()
        max_len = max([len(v) for v in dgs.values()])
        extend = lambda vals: [vals[i] if i < len(vals) else np.NaN for i in range(max_len)]
        df =  pd.DataFrame.from_dict({k:extend(v) for k,v in dgs.items()})
        
        return df

class ElementsResults(Collection):
    """Intra Only
    Elements Results covers all the elements in a manoeuvre
    """
    VType=Results
    uid="name"

    def downgrade(self):
        return sum(er.downgrade() for er in self)
    
    def downgrade_list(self):
        return [er.results.downgrade() for er in self]
    
    def downgrade_df(self):
        df = pd.concat([idg.downgrade_df().sum() for idg in self], axis=1).T
        df["Total"] = df.T.sum()
        df["Element"] = self.data.keys()
        
        return df.set_index("Element")