
from flightanalysis.base.constructs import Constructs, SVar
from geometry import Point, Quaternion, Quaternions, Points
import numpy as np



def make_dt(sec) -> np.array:
    return np.gradient(sec.data.index)


def make_error(sec):
    raise NotImplementedError("cant construct a section without time, pos and att data")


contvars = Constructs({
    "time":  SVar("t",         ["t"],                                          float,      np.array,    make_error, ""),
    "dt":    SVar("dt",        ["dt"],                                         float,      np.array,    make_dt,    ""),
    "inputs":   SVar("inputs",    ["throttle", "aileron_1", "aileron_2", "elevator", "rudder"],  np.array,   np.array,    make_error, ""),
})
