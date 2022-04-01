from flightanalysis.base.table import Table, Time, SVar
from typing import Union
from flightdata import Flight, Fields
from pathlib import Path
from flightanalysis.base.constructs import Constructs, SVar
from geometry import Point, Quaternion, Quaternions, Points
import numpy as np
from flightanalysis.state import State
from flightanalysis.model.flow import Flow
from flightanalysis.model.constants import ACConstants


class Coefficients(Table):
    constructs = Table.constructs + Constructs(dict(
        force = SVar(Point, ["cx", "cy", "cz"], None),
        moment = SVar(Point, ["cl", "cm", "cn"], None)
    ))

    @staticmethod
    def build(sec: State, flow: Flow, consts: ACConstants):
        I = consts.inertia
        u = sec.vel
        du = sec.acc
        w = sec.rvel
        dw = sec.racc
        moment=I*(dw + w.cross(w)) / (flow.q * consts.s) 
        #not correct need to extend geometry module to include inertia matrix

        return Coefficients.from_constructs(
            sec.time,
            force=(du + w.cross(u)) * consts.mass / (flow.q * consts.s),
            moment=moment / Point(consts.b, consts.c, consts.b).tile(len(moment))
        )



