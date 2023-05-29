from __future__ import annotations
import numpy as np
import pandas as pd

from geometry import Base,  Point, Quaternion, Transformation
from typing import Union, Dict
from .constructs import SVar, Constructs
from numbers import Number
from time import time

class Time(Base):
    cols=["t", "dt"]
    
    @staticmethod
    def from_t(t: np.ndarray):
        if isinstance(t, Number):
            return Time(t, 1/30)
        else:
            dt = np.array([1/30]) if len(t) == 1 else np.gradient(t)
            return Time(t, dt)

    def scale(self, duration):
        old_duration = self.t[-1] - self.t[0]
        sfac = duration / old_duration
        return Time(
            self.t[0] + (self.t - self.t[0]) * sfac,
            self.dt * sfac
        )

    def reset_zero(self):
        return Time(self.t - self.t[0], self.dt)


    @staticmethod
    def now():
        return Time.from_t(time())



def make_time(tab):
    return Time.from_t(tab.t)
    
class Table:
    constructs = Constructs([
         SVar("time", Time,        ["t", "dt"]               , make_time )
    ])

    def __init__(self, data: pd.DataFrame, fill=True):
        if len(data) == 0:
            raise Exception("Created with empty dataframe")
            
        self.data = data

        self.data.index = self.data.index - self.data.index[0]
        
        if fill:
            missing = self.constructs.missing(self.data.columns)
            for svar in missing:
                
                newdata = svar.builder(self).to_pandas(
                    columns=svar.keys, 
                    index=self.data.index
                ).loc[:, [key for key in svar.keys if key not in self.data.columns]]
                
                self.data = pd.concat([self.data, newdata], axis=1)
    
    def __getattr__(self, name: str) -> Union[pd.DataFrame, Base]:
        if name in self.data.columns:
            return self.data[name].to_numpy()
        elif name in self.constructs.data.keys():
            con = self.constructs.data[name]
            return con.obj(self.data.loc[:, con.keys])
        else:
            raise AttributeError(f"Unknown column or construct {name}")

    def to_csv(self, filename):
        self.data.to_csv(filename)
        return filename

    def __len__(self):
        return len(self.data)


    @property
    def duration(self):
        return self.data.index[-1] - self.data.index[0]


    def __getitem__(self, sli):
        if isinstance(sli, int) or isinstance(sli, float): 
            if sli==-1:
                return self.__class__(self.data.iloc[[-1], :])

            return self.__class__(
                self.data.iloc[self.data.index.get_indexer([sli], method="nearest"), :]
            )
        
        return self.__class__(self.data.loc[sli])


    def __iter__(self):
        for ind in list(self.data.index):
            yield self[ind]

    @classmethod
    def from_constructs(cls, *args,**kwargs):
        kwargs = dict(
            **{list(cls.constructs.data.keys())[i]: arg for i, arg in enumerate(args)},
            **kwargs
        )

        df = pd.concat(
            [
                x.to_pandas(
                    columns=cls.constructs[key].keys, 
                    index=kwargs["time"].t
                ) for key, x in kwargs.items() if not x is None
            ],
            axis=1
        )

        return cls(df)

    def __repr__(self):
        return f"{self.__class__.__name__} Table, duration = {self.duration}\n{self.data}"


    def copy(self, *args,**kwargs):
        kwargs = dict(kwargs, **{list(self.constructs.data.keys())[i]: arg for i, arg in enumerate(args)}) # add the args to the kwargs

        old_constructs = {key: self.__getattr__(key) for key in self.constructs.existing(self.data.columns).data if not key in kwargs}
        
        new_constructs = {key: value for key, value in list(kwargs.items()) + list(old_constructs.items())}

        return self.__class__.from_constructs(**new_constructs)


    def label(self, **kwargs):
        return self.__class__(self.data.assign(**kwargs))

    def remove_labels(self):
        return self.__class__(
            self.data.drop(
                [c for c in self.data.columns if not c in self.constructs.cols], 
                1, 
                errors="ignore"
            )
        )
    

    def append(self, other, timeoption:str="dt"):

        if timeoption in ["now", "t"]:
            t = np.array([time()]) if timeoption == "now" else other.t
            dt = other.dt
            dt[0] = t[0] - self.t[-1]
            new_time = Time(t, dt)
        elif timeoption == "dt":
            new_time = Time(other.t + self[-1].t - other[0].t + other[0].dt, other.dt)

        return self.__class__(pd.concat(
            [
                self.data, 
                other.copy(new_time).data
            ], 
            axis=0, 
            ignore_index=True
        ).set_index("t", drop=False))
    