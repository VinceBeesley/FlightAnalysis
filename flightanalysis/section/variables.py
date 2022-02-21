from flightanalysis.base.constructs import Constructs, SVar
from geometry import Point, Quaternion, Quaternions, Points
import numpy as np


constructs = Constructs({
    "time":     SVar("t",       ["t"],                      float,          np.array,       lambda : 0.0,                           ""),
    "dt":       SVar("dt",      ["dt"],                     float,          np.array,       lambda : 0.0,                           ""),
    "pos":      SVar("",        ["x", "y", "z"],            Point,          Points,         Point.zeros,                            ""),
    "att":      SVar("r",       ["rw", "rx", "ry", "rz"],   Quaternion,     Quaternions,    Quaternion.zero,   "Body Axis Orientation"),
    "bvel":     SVar("bv",      ["bvx", "bvy", "bvz"],      Point,          Points,         Point.zeros,                            ""),
    "brvel":    SVar("brv",     ["brvr", "brvp", "brvy"],   Point,          Points,         Point.zeros,                            ""),
    "bacc":     SVar("ba",      ["bax", "bay", "baz"],      Point,          Points,         Point.zeros,                            ""),
    "bracc":    SVar("bra",     ["brar","brap", "bray"],    Point,          Points,         Point.zeros,                            ""),
})
