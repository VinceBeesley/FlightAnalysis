from __future__ import annotations
from typing import Any, Dict, List, Union
import numpy as np
import numpy.typing as npt
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
    sample: npt.ArrayLike  # the comparison built from the measurement
    errors: npt.ArrayLike  # the errors resulting from the comparison
    dgs: npt.ArrayLike # downgrades for the errors
    keys: npt.ArrayLike # links from dgs to sample index

    @property
    def total(self):
        return sum(self.dgs)
    
    def to_dict(self):
        return dict(
            name = self.name,
            measurement = self.measurement.to_dict() if isinstance(self.measurement, Measurement) else list(self.measurement),
            sample=self.sample,
            errors=self.errors,
            dgs = self.dgs, 
            keys = self.keys,
            total = self.total
        )
    
    def __repr__(self):
        return f'Result({self.name}, {self.errors}, {self.dgs})'
    
    @staticmethod
    def from_dict(data) -> Result:
        return Result(
            data['name'],
            Measurement.from_dict(data['measurement']) if isinstance(data['measurement'], dict) else np.array(data['measurement']),
            np.array(data['sample']),
            np.array(data['errors']),
            np.array(data['dgs']),
            data['keys']
        )

    def info(self, i: int):
        return f'downgrade={np.round(self.dgs[i], 3)}\nerror={np.round(self.errors[i],3)}\nvisibility={np.round(self.measurement.visibility[self.keys[i]], 2)}'

    def summary_df(self):
        return pd.DataFrame(
            np.column_stack([self.keys, self.sample, self.errors, self.measurement.visibility, self.dgs]),
            columns = ['collector', 'value', 'error', 'visibility', 'downgrade']
        )

    def plot(self):
        import plotly.graph_objects as go
        fig=go.Figure(layout=dict(
            yaxis=dict(title='measurement'), 
            yaxis2=dict(title='visibility', overlaying="y")
        ))
        
        x=list(range(0, len(self.measurement),1))
        fig.add_trace(go.Scatter(x=x,y=abs(self.measurement.value), name='flown'))

        fig.add_trace(go.Scatter(
            x=x, y=self.sample, 
            name='sample', yaxis='y',
            line=dict(width=3, color='black')
        ))

        hovtxt=[self.info(i) for i in range(len(self.keys))]

        fig.add_trace(go.Scatter(
            x=self.keys, y=self.sample[self.keys],
            text=np.round(self.dgs, 3),
            hovertext=hovtxt,
            mode='markers+text',
            name='downgrades',
            yaxis='y'
        ))

        fig.add_trace(go.Scatter(
            x=x, y=self.measurement.visibility, name='visibility',yaxis='y2'))

        return fig
    
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

    @property
    def total(self):
        return sum([cr.total for cr in self])

    def downgrade_summary(self):
        return {r.name: r.dgs for r in self if len(r.dgs) > 0}

    def downgrade_df(self) -> pd.DataFrame:
        dgs = self.downgrade_summary()
        if len(dgs) == 0:
            return pd.DataFrame()
        max_len = max([len(v) for v in dgs.values()])
        extend = lambda vals: [vals[i] if i < len(vals) else np.NaN for i in range(max_len)]
        df =  pd.DataFrame.from_dict({k:extend(v) for k,v in dgs.items()})
        
        return df

    def to_dict(self) -> Dict[str, dict]:
        return dict(
            name = self.name,
            data = {k: v.to_dict() for k, v in self.data.items()},
            summary = self.downgrade_summary(),
            total = self.total
        )

    @staticmethod
    def from_dict(data) -> Results:
        return Results(
            data['name'],
            [Result.from_dict(v) for v in data['data'].values()]
        )


class ElementsResults(Collection):
    """Intra Only
    Elements Results covers all the elements in a manoeuvre
    """
    VType=Results
    uid="name"

    @property
    def total(self):
        return sum(self.downgrade_list)
    
    @property
    def downgrade_list(self):
        return [er.total for er in self]
    
    def downgrade_df(self):
        df = pd.concat([idg.downgrade_df().sum() for idg in self], axis=1).T
        df["Total"] = df.T.sum()
        df["Element"] = self.data.keys()
        
        return df.set_index("Element")
    
    def to_dict(self) -> Dict[str, dict]:
        return dict(
            data = {k: v.to_dict() for k, v in self.data.items()},
            summary = self.downgrade_list,
            total = self.total
        )

    @staticmethod
    def from_dict(data) -> Results:
        return Results(
            [Result.from_dict(v) for v in data['data'].values()]
        )
