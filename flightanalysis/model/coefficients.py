from flightanalysis.base import Period, make_dt, make_error
from typing import Union
from flightdata import Flight, Fields
from pathlib import Path
from flightanalysis.base.constructs import Constructs, SVar
from geometry import Point, Quaternion, Quaternions, Points
import numpy as np
from flightanalysis.section import Section
from flightanalysis.model.flow import Flow
from flightanalysis.model.constants import ACConstants

coefvars = Constructs({
    "time":    SVar("t",   ["t"],                  float,  np.array, make_error, ""),
    "dt":      SVar("dt",  ["dt"],                 float,  np.array, make_dt,    ""),
    "force":   SVar("force", ["cx", "cy", "cz"],  Point,  Points,   make_error, ""),
    "moment":  SVar("moment",["cl", "cm", "cn"],  Point,  Points,   make_error, ""),
})


class Coefficients(Period):
    _cols = coefvars

    @staticmethod
    def build(sec: Section, flow: Flow, consts: ACConstants):
        return Coefficients.from_constructs(
            time=sec.gtime,
            force=sec.gbacc * consts.mass / (flow.gq * consts.s),
            moment=sec.gbracc * consts.inertia / (flow.gq * consts.s * consts.c) 
        )

class Coefficient(Period):
    _cols = coefvars
    Period = Coefficients



Coefficients.Instant = Coefficient