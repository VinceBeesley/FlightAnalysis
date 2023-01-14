import numpy as np
from geometry import Transformation, Point, Quaternion, PX, PY, PZ
from flightanalysis.state import State
from flightanalysis.base.table import Time
from . import El, Loop, DownGrades, DownGrade, Elements
from flightanalysis.criteria import *
from typing import Union


class Autorotation(El):
    """much like a line, but rolls happens around the velocity vector,
    rather than the body x axis"""
    parameters = El.parameters + "length,roll,rate".split(",")
    def __init__(self, speed: float, length: float, roll: float, uid: str):
        super().__init__(uid, speed)
        self.length = length
        self.roll = roll
    
    @property
    def angle(self):
        return 2 * np.pi * self.roll

    @property
    def rate(self):
        return self.angle * self.speed / self.length

    def create_template(self, istate: State, flown: State=None):
        return istate.copy(vel=istate.vel.scale(self.speed)).fill(
            El.create_time(self.length / self.speed, flown)
        ).superimose_rotation(
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