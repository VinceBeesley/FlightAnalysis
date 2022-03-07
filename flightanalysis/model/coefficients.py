from winreg import ExpandEnvironmentStrings
from flightanalysis.base import Period, make_dt, make_error
from typing import Union
from flightdata import Flight, Fields
from pathlib import Path
from flightanalysis.base.constructs import Constructs, SVar
from geometry import Point, Quaternion, Quaternions, Points
import numpy as np


coefvars = Constructs({
    "time":    SVar("t",   ["t"],                  float,  np.array, make_error, ""),
    "dt":      SVar("dt",  ["dt"],                 float,  np.array, make_dt,    ""),
    "force":   SVar("force", ["cx", "cy", "cz"],  Point,  Points,   make_error, ""),
    "moment":  SVar("moment",["cl", "cm", "cn"],  Point,  Points,   make_error, ""),
})


class Coefficients(Period):
    _cols = coefvars

class Coefficient(Period):
    _cols = coefvars
    Period = Coefficients

Coefficients.Instant = Coefficient