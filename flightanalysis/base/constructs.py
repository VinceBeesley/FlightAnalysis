"""These are the variables handled by the State and Section classes.
    The variables are defined in the values of the svars dict, in the order in which they first appear.
    The keys just provide some handy tags to access sets of values with. 

    pos = position (Cartesian)
    att = attitude (Quaternion)
    bvel = velocity in (body frame)
    brvel = rotational velocity (body axis rates)

    """
import numpy as np
import pandas as pd
from typing import List, Dict, Union


class SVar:
    def __init__(self, obj, keys=None, builder=None):
        self.obj = obj
        self.keys = obj.cols if keys is None else keys
        self.builder = builder


class Constructs:
    def __init__(self, data: Dict[str, SVar]):
        self.data = data
        self.cols = [name for sv in self.data.values() for name in sv.keys]

    def subset(self, names: List[str]):
        """get a subset of the constructs"""
        return Constructs({key: value for key, value in self.data.items() if key in names})

    def existing(self, vars: List[str]):
        """return a subset that is fully populated by the list of keys input"""
        return self.subset([
            key for key, value in self.data.items() 
            if all(val in vars for val in value.keys)
        ])

    def missing(self, vars: List[str]):
        """return a subset that has not been populated by the list of vars"""
        return self.subset([
            key for key, value in self.data.items() 
            if not all(val in vars for val in value.keys)
        ])

    def to_list(self):
        return list(self.data.values())

    def contains(self, names: Union[list, str]) -> bool:
        _names = [names] if isinstance(names, str) else names
        
        keys = self.data.keys()
        res = [name in keys for name in _names]
        return res[0] if isinstance(names, str) else res

    def cdicts(self, **kwargs):
        return [self.data[key].todict(const) for key, const in list(kwargs.items())]        

    def __add__(self, other):
        return Constructs(dict(**self.data, **other.data))

    def __iter__(self):
        for val in self.data.values():
            yield val
