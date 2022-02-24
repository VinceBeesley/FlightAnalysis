from flightanalysis.base.constructs import Constructs, SVar
from geometry import Point, Quaternion, Quaternions, Points
import numpy as np




def make_dt(sec) -> np.array:
    return np.gradient(sec.data.index)

def make_bvel(sec) -> Points:
    wvel = sec.gpos.diff(sec.gdt)
    return sec.gatt.inverse().transform_point(wvel)

def make_brvel(sec) -> Points:
    return sec.gatt.body_diff(sec.gdt).remove_outliers(3) 

def make_bacc(sec) -> Points:
    wacc = sec.gatt.transform_point(sec.gbvel).diff(sec.gdt) + Point(0, 0, 9.81) # assumes world Z is up
    return sec.gatt.inverse().transform_point(wacc)

def make_bracc(sec) -> Points:
    return sec.gbrvel.diff(sec.gdt)

def make_error(sec):
    raise NotImplementedError("cant construct a section without time, pos and att data")



secvars = Constructs({
    "time":  SVar("t",   ["t"],                    float,      np.array,    make_error, ""),
    "dt":    SVar("dt",  ["dt"],                   float,      np.array,    make_dt,    ""),
    "pos":   SVar("",    ["x", "y", "z"],          Point,      Points,      make_error, ""),
    "att":   SVar("r",   ["rw", "rx", "ry", "rz"], Quaternion, Quaternions, make_error, "Body Axis Orientation"),
    "bvel":  SVar("bv",  ["bvx", "bvy", "bvz"],    Point,      Points,      make_bvel,  ""),
    "brvel": SVar("brv", ["brvr", "brvp", "brvy"], Point,      Points,      make_brvel, ""),
    "bacc":  SVar("ba",  ["bax", "bay", "baz"],    Point,      Points,      make_bacc,  ""),
    "bracc": SVar("bra", ["brar","brap", "bray"],  Point,      Points,      make_bracc, ""),
})
