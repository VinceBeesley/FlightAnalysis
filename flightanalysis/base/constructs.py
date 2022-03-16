"""These are the variables handled by the State and Section classes.
    The variables are defined in the values of the svars dict, in the order in which they first appear.
    The keys just provide some handy tags to access sets of values with. 

    pos = position (Cartesian)
    att = attitude (Quaternion)
    bvel = velocity in (body frame)
    brvel = rotational velocity (body axis rates)

    """
from geometry import Point, Points, Quaternion, Quaternions, Transformation
import numpy as np
import pandas as pd
from typing import List, Dict, Union


todict = {
    Point: lambda x, keys: {key: value for key, value in zip(keys, x.to_list())},
    Quaternion: lambda x, keys: {key: value for key, value in zip(keys, x.to_list())},
    float: lambda x, keys: {keys[0]: x}
}

fromdict = {
    Point: lambda x: Point(*x.values()),
    Quaternion: lambda x: Quaternion(*x.values()),
    float: lambda x: list(x.values())[0]
}

todf = {
    Points: lambda x, index, columns: x.to_pandas(columns=columns, index=index),
    Quaternions: lambda x, index, columns: x.to_pandas(columns=columns, index=index),
    np.array: lambda x, index, columns: pd.DataFrame(np.array(x), columns=columns, index=index),
}

fromdf = {
    Points: lambda x: Points.from_pandas(x),
    Quaternions: lambda x: Quaternions.from_pandas(x),
    np.array: lambda x: np.array(x)[:,0]
}

class SVar:
    def __init__(self, keys, Single, Multiple, default):
        #self.name = name
        self.keys = keys
        self.default = default
        self.todict = lambda x : todict[Single](x, self.keys)
        self.fromdict = lambda x : fromdict[Single]({key: x[key] for key in self.keys})
        self.todf = lambda x, index: todf[Multiple](x, index, self.keys)
        self.fromdf = lambda x: fromdf[Multiple](x.loc[:,self.keys])

class Constructs:
    def __init__(self, data: Dict[str, SVar]):
        self.data = data
        self.gdata = {"g" + key: value for key, value in self.data.items()}
        self.vars = [name for sv in self.data.values() for name in sv.keys]

    def subset(self, names: List[str]):
        """get a subset of the constructs dict"""
        return Constructs({key: value for key, value in self.data.items() if key in names})


    def existing(self, vars: List[str]):
        """return a subset that is fully populated by the list of vars input"""
        return self.subset([key for key, value in self.data.items() if all(val in vars for val in value.keys)])

    def missing(self, vars: List[str]):
        #return a subset that has not been populated by the list of vars
        return self.subset([key for key, value in self.data.items() if not all(val in vars for val in value.keys)])

    def to_list(self):
        return [value for value in self.data.values()]

    def contains(self, names: Union[list, str]) -> bool:
        
        _names = [names] if isinstance(names, str) else names
        
        keys = self.data.keys()
        res = [name in keys for name in _names]
        return res[0] if isinstance(names, str) else res

    def cdicts(self, **kwargs):
        return [self.data[key].todict(const) for key, const in list(kwargs.items())]        
