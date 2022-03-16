from flightanalysis.base import Period, make_dt, make_error, default_vars, Instant
from typing import Union
from flightdata import Flight, Fields
from pathlib import Path
from flightanalysis.base.constructs import Constructs, SVar
from geometry import Point, Quaternion, Quaternions, Points
import numpy as np
from flightanalysis.section import Section
from flightanalysis.model.flow import Flow
from flightanalysis.model.constants import ACConstants

coefvars = Constructs(dict(**default_vars, **{
    "force":   SVar(["cx", "cy", "cz"],  Point,  Points,   make_error),
    "moment":  SVar(["cl", "cm", "cn"],  Point,  Points,   make_error),
}))

class Coefficients(Period):
    _cols = coefvars

    @staticmethod
    def build(sec: Section, flow: Flow, consts: ACConstants):
        I = consts.inertia
        u = sec.gbvel
        du = sec.gbacc
        w = sec.gbrvel
        dw = sec.gbracc
        moment=I*(dw + w.cross(w)) / (flow.gq * consts.s) 
        #not correct need to extend geometry module to include inertia matrix

        return Coefficients.from_constructs(
            time=sec.gtime,
            force=(du + u.cross(u)) * consts.mass / (flow.gq * consts.s),
            moment=moment / Points.full(Point(consts.b, consts.c, consts.b), moment.count)
        )

class Coefficient(Instant):
    _cols = coefvars
    Period = Coefficients



Coefficients.Instant = Coefficient