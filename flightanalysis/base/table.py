import numpy as np
import pandas as pd

from geometry import Base,  Point, Quaternion, Transformation
from typing import Union, Dict
from .constructs import SVar, Constructs



class Time(Base):
    cols=["t", "dt"]
 

def make_time(tab):
    dt = np.gradient(tab.t) if len(tab.t) > 1 else 1/30
    return Time(tab.t,dt)


class Table:
    constructs = Constructs(dict(
        time = SVar(Time,        ["t", "dt"]               , make_time )
    ))

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
                self.data.iloc[[self.data.index.get_loc(sli, method="nearest")], :]
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
                    columns=cls.constructs.data[key].keys, 
                    index=kwargs["time"]
                ) for key, x in kwargs.items()
            ],
            axis=1
        )

        return cls(df)




    def copy(self, *args,**kwargs):
        kwargs = dict(kwargs, **{list(self.constructs.data.keys())[i]: arg for i, arg in enumerate(args)}) # add the args to the kwargs

        old_constructs = {key: self.__getattr__(key) for key in self.constructs.existing(self.data.index).data if not key in kwargs}
        
        new_constructs = {key: value for key, value in list(kwargs.items()) + list(old_constructs.items())}

        return State.from_constructs(**new_constructs)



class State(Table):
    constructs = Table.constructs + Constructs(dict(
        pos  = SVar(Point,       ["x", "y", "z"]           , None ), 
        att  = SVar(Quaternion,  ["rw", "rx", "ry", "rz"]  , None ),
        vel  = SVar(Point,       ["u", "v", "w"]           , None ),
        rvel = SVar(Point,       ["p", "q", "r"]           , None ),
        acc  = SVar(Point,       ["du", "dv", "dw"]        , None ),
        racc = SVar(Point,       ["dp", "dq", "dr"]        , None ),
    ))
