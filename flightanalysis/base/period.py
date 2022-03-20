
from geometry import Point, Quaternion
from .constructs import Constructs
import numpy as np
import pandas as pd
from typing import Union
from numbers import Number

from abc import ABC, abstractmethod

class Period(ABC):
    _construct_freq = 30

    def __init__(self, data: pd.DataFrame):
        if len(data) == 0:
            raise Exception("Section created with empty dataframe")
        self.data = data
        self.data.index = self.data.index - self.data.index[0]
        
        missing = self.cols.missing(self.data.columns)

        for svar in missing.data.values():
            self.data = pd.concat([
                self.data, 
                svar.todf(svar.default(self), self.data.index)
            ], axis=1)
        
        assert len(self.cols.missing(self.data.columns).data) == 0

    @property
    def _Instant(self):
        return self.__class__.Instant

    @property
    def cols(self):
        return self.__class__._cols

    def __getattr__(self, name) -> Union[pd.DataFrame, Point, Quaternion]:
        if name in self.data.columns:
            return self.data[name]
        elif name in self.cols.data.keys():
            return self.data[self.cols.data[name].keys]
        elif name == "gtime":     
            return self.time.to_numpy()[:,0]
        elif name in self.cols.gdata.keys():
            return self.cols.data[name[1:]].fromdf(self.data)

    def segment(self, partitions):
        parts = np.linspace(self.data.index[0], self.data.index[-1], partitions)

        return [
            self.subset(p0, p1) 
            for p0, p1 in 
            zip(parts[:-2], parts[1:])
        ]
       
    def append_columns(self, data):
        if isinstance(data, list):
            return self.__class__(pd.concat([self.data] + data, axis=1, join="inner"))
        elif isinstance(data,pd.DataFrame):
            return self.__class__(pd.concat([self.data, data], axis=1, join="inner"))
        elif isinstance(data, pd.Series):
            return self.__class__(pd.concat([self.data, data], axis=1, join="inner"))
            
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
                return self._Instant(self.data.iloc[-1])
            return self._Instant(self.data.iloc[self.data.index.get_loc(sli, method="nearest")])
        return self.__class__(self.data.loc[sli])

    def __iter__(self):
        for ind in list(self.data.index):
            yield self[ind]

    def get_state_from_index(self, index):
        return self._Instant(self.data.iloc[index])

    def subset(self, start, end):
        if start==-1 and end==-1:
            return self
        if start==-1:
            return self[:end]
        if end==-1:
            return self[start:]
        return self[start:end]

    @classmethod
    def from_constructs(cls, *args,**kwargs):
        kwargs = dict(kwargs, **{list(cls._cols.data.keys())[i]: arg for i, arg in enumerate(args)})
        df = pd.concat(
            [cls._cols.data[key].todf(x, kwargs["time"]) for key, x in kwargs.items()],
            axis=1
        )

        return cls(df)

    
    def copy(self, *args, **kwargs):
        kwargs = dict(kwargs, **{list(self.cols.data.keys())[i]: arg for i, arg in enumerate(args)})
        
        old_constructs = {key: self.__getattr__("g" + key) for key in self.cols.existing(self.data.columns) if not key in kwargs.keys()}

        new_constructs = {key: value for key, value in list(kwargs.items()) + list(old_constructs.items())}

        return self.__class__.from_constructs(**new_constructs).append_columns(self.data[self.misc_cols()])
