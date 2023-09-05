from __future__ import annotations
import numpy as np
from geometry import Transformation, Point, Quaternion, PX, PY, PZ, P0
from flightanalysis import State
from flightanalysis.base.table import Time
from .element import Element, Elements
from flightanalysis.schedule.scoring.criteria.f3a_criteria import F3A
from flightanalysis.schedule.scoring import Measurement, DownGrade, DownGrades
from typing import Union


class Autorotation(Element):
    """much like a line, but rolls happens around the velocity vector,
    rather than the body x axis"""
    parameters = Element.parameters + "length,roll,rate,angle".split(",")
    def __init__(self, speed: float, length: float, roll: float, uid: str):
        super().__init__(uid, speed)
        self.length = length
        self.roll = roll
        
    @property
    def intra_scoring(self):
        return DownGrades([DownGrade(Measurement.roll_angle, F3A.single.roll)])
    
    @property
    def angle(self):
        return 2 * np.pi * self.roll

    @property
    def rate(self):
        return self.angle * self.speed / self.length
    
    def create_template(self, istate: State, time: Time=None):
        
        return istate.copy(
            vel=istate.vel.scale(self.speed),
            rvel=P0()
        ).fill(
            Element.create_time(self.length / self.speed, time)
        ).superimpose_rotation(
            istate.vel.unit(),
            self.angle
        ).label(element=self.uid)
    
    def describe(self):
        d1 = f"autorotation {self.roll} turns"
        return f"{d1}, length = {self.length} m"

    def match_intention(self, transform: Transformation, flown: State):
        # TODO this assumes the plane is traveling forwards, create_template does not
        jit = flown.judging_itrans(transform)
        
        return self.set_parms(
            length=jit.att.inverse().transform_point(flown.pos - jit.pos).x[-1],
            roll=np.sign(np.mean(flown.p)) * abs(self.roll),
            speed=np.mean(abs(flown.vel))
        )
    
    def copy_direction(self, other: Autorotation) -> Autorotation:
        return self.set_parms(roll=abs(self.roll) * np.sign(other.roll))


        