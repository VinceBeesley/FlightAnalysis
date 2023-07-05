from __future__ import annotations
import numpy as np
from geometry import Transformation, PX, PY, PZ
from flightanalysis.state import State
from flightanalysis.base.table import Time
from .element import Element
from .line import Line
from flightanalysis.schedule.scoring import *


class Recovery(Element):
    parameters = Element.parameters + ["length"]
    def __init__(self, speed, length, uid: str=None):
        super().__init__(uid, speed)
        self.length = length

    def to_dict(self):
        return dict(
            kind=self.__class__.__name__,
            speed=self.speed,
            length=self.length,
            uid=self.uid
        )

    def create_template(self, istate: State, time: Time=None) -> State:
        return Line(self.speed, self.length).create_template(
            istate, 
            time
        ).superimpose_rotation(
            PY(),
            -np.arctan2(istate.vel.z, istate.vel.x)[-1]
        ).label(element=self.uid)

    def describe(self):
        return "recovery"

    def match_intention(self, transform: Transformation, flown: State) -> Recovery:
        jit = flown.judging_itrans(transform)
        return self.set_parms(
            length=max(jit.att.inverse().transform_point(flown.pos - jit.pos).x[-1], 5),
            speed=abs(flown.vel).mean()
        )
    
    def copy_direction(self, other: Recovery) -> Recovery:
        return self.set_parms()

    @property
    def intra_scoring(self) -> DownGrades:
        return DownGrades()

    @property
    def exit_scoring(self) -> DownGrades:
        return DownGrades()
