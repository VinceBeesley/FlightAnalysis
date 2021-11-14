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
    np.array: lambda x, index, columns: pd.DataFrame(np.array(x), columns=columns, index=index)
}
fromdf = {
    Points: lambda x: Points.from_pandas(x),
    Quaternions: lambda x: Quaternions.from_pandas(x),
    np.array: lambda x: np.array(x)
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


constructs = {
    "time":     SVar("t",       ["t"],                      float,          np.array,       lambda : 0.0,               ""),
    "pos":      SVar("",        ["x", "y", "z"],            Point,          Points,         Point.zeros,                ""),
    "att":      SVar("r",       ["rw", "rx", "ry", "rz"],   Quaternion,     Quaternions,    Quaternion.zero,            ""),
    "bvel":     SVar("bv",      ["bvx", "bvy", "bvz"],      Point,          Points,         Point.zeros,                ""),
    "brvel":    SVar("brv",     ["brvr", "brvp", "brvy"],   Point,          Points,         Point.zeros,                ""),
    "bacc":     SVar("ba",      ["bax", "bay", "baz"],      Point,          Points,         Point.zeros,                ""),
    "wind":     SVar("wv",      ["wvx", "wvy", "wvz"],      Point,          Points,         Point.zeros,                ""),
    "bwind":    SVar("bwv",     ["bwvx", "bwvy", "bwvz"],   Point,          Points,         Point.zeros,                ""),
    "alpha":    SVar("alpha",   ["alpha"],                  float,          np.array,       lambda : 0.0,               ""),
    "beta":     SVar("beta",    ["beta"],                   float,          np.array,       lambda : 0.0,               ""),
}


def subset_constructs(names):
    return [value for key, value in constructs.items() if key in names]

def subset_vars(consts):
    return [name for sv in subset_constructs(consts) for name in sv.keys]

all_vars = subset_vars(constructs.keys())

essential = ["time", "pos", "att", "bvel", "brvel"]
essential_keys = subset_vars(essential)


defaults = dict(
    time= Point.zeros(),

)

def assert_vars(keys):
    assert set(essential_keys).issubset(keys), "missing essential keys {}".format(
            [key for key in essential_keys if not key in keys]
    )

def missing_constructs(names):
    return [key for key in essential if not key in names]

def assert_constructs(names):
    assert set(essential).issubset(names), "missing essential constructs {}, got {}".format(
        missing_constructs(names), names
    )

def default_constructs(names):
    return {name:constructs[name].default() for name in names}