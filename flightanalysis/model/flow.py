
from flightanalysis.base import Period, make_dt, make_error
from typing import Union
from flightdata import Flight, Fields
from pathlib import Path
from flightanalysis.base.constructs import Constructs, SVar
from geometry import Point, Quaternion, Quaternions, Points
import numpy as np


flowvars = Constructs({
    "time":  SVar("t",   ["t"],               float,      np.array,    make_error, ""),
    "dt":    SVar("dt",  ["dt"],              float,      np.array,    make_dt,    ""),
    "aoa":   SVar("aoa", ["alpha", "beta"],   np.array,   np.array,    make_error, ""),
})


class Flows(Period):
    _cols = flowvars


class Flow(Period):
    _cols = flowvars
    Period = Flows

Flows.Instant = Flow