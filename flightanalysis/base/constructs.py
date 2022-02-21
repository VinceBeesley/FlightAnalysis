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
from typing import List, Dict


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
    def __init__(self, name, keys, Single, Multiple, default, description):
        self.name = name
        self.keys = keys
        self.default = default
        self.todict = lambda x : todict[Single](x, self.keys)
        self.fromdict = lambda x : fromdict[Single]({key: x[key] for key in self.keys})
        self.todf = lambda x, index: todf[Multiple](x, index, self.keys)
        self.fromdf = lambda x: fromdf[Multiple](x.loc[:,self.keys])
        self.description = description



class Constructs:
    def __init__(self, constructs: Dict(str, SVar)):
        self.constructs = constructs
        self.all_vars = self.subset_vars(self.constructs.keys())   

    def subset_constructs(self, names: List[str]):
        """get a subset of the constructs dict"""
        return [value for key, value in self.constructs.items() if key in names]

    def subset_vars(self, consts: List[str]):
        """get a list of the column names contained in the requested subset of constructs"""
        return [name for sv in self.subset_constructs(consts) for name in sv.keys]

    def construct_list(self, vars):
        return [key for key, const in self.constructs.items() if all([val in vars for val in const.keys])]


    def missing_constructs(self, names):
        """get a list of the missing construct names in the input list"""
        return [key for key in self.constructs.keys() if not key in names]


    def default_constructs(self, names):
        return {name:self.constructs[name].default() for name in names}


    def cdicts(self, **kwargs):
        return [self.constructs[key].todict(const) for key, const in list(kwargs.items())]        

    def existing_constructs(self, names):
        return [key for key, const in self.constructs.items() if all([val in names for val in const.keys])] 