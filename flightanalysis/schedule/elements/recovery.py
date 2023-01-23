import numpy as np
from geometry import Transformation, Point, Quaternion, PX, PY, PZ
from flightanalysis.state import State
from flightanalysis.base.table import Time
from . import El, Loop, DownGrades, DownGrade, Elements, Line
from flightanalysis.criteria import *



class Recovery(El):
    parameters = El.parameters + ["length"]
    def __init__(self, speed, length, uid: str=None):
        super().__init__(uid, speed)
        self.length = length

    def create_template(self, istate: State, flown: State=None):
        


        return Line(self.speed, self.length).create_template(
            istate, 
            flown
        ).superimpose_rotation(
            PY(),
            -np.arctan2(istate.vel.z, istate.vel.x)[-1]
        )

    def match_intention(self, transform: Transformation, flown: State):
        jit = flown.judging_itrans(transform)
        return self.set_parms(
            length=jit.att.inverse().transform_point(flown.pos - jit.pos).x[-1],
            speed=abs(flown.vel).mean()
        )