from __future__ import annotations
import numpy as np
from geometry import Transformation, PX, PY, PZ
from flightanalysis.state import State
from flightanalysis.base.table import Time
from .element import Element
from flightanalysis.schedule.scoring.criteria.f3a_criteria import F3A
from flightanalysis.schedule.scoring import Measurement, DownGrade, DownGrades
from .line import Line


class PitchBreak(Element):
    parameters = Element.parameters + "length,break_angle".split(",")
    def __init__(self, speed: float, length: float, break_angle: float, uid: str=None):
        super().__init__(uid, speed)
        self.length=length
        self.break_angle = break_angle

    def create_template(self, istate: State, time: Time=None) -> State:
        return Line(self.speed, self.length).create_template(
            istate, 
            time
        ).superimpose_rotation(
            PY(),
            self.break_angle
        ).label(element=self.uid)

    def describe(self):
        return "pitch break"
    
    def match_intention(self, transform: Transformation, flown: State) -> PitchBreak:
        jit = flown.judging_itrans(transform)

        _speed = abs(flown.vel).mean()

        alphas = np.arctan2(flown.vel.z, flown.vel.x)

        return self.set_parms(
            speed = _speed,
            length = max(
                jit.att.inverse().transform_point(flown.pos - jit.pos).x[-1],
                5
            ) ,
            break_angle = alphas[-1]
        )
    
    def copy_direction(self, other: PitchBreak) -> PitchBreak:
        return self.set_parms(break_angle=abs(self.break_angle) * np.sign(other.break_angle))


    @property
    def intra_scoring(self) -> DownGrades:
        return DownGrades()

    @property
    def exit_scoring(self) -> DownGrades:
        return DownGrades()
