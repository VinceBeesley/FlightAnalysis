import numpy as np
from geometry import Transformation, Point, Quaternion, PX, PY, PZ
from flightanalysis.state import State
from flightanalysis.base.table import Time
from . import El, Loop, DownGrades, DownGrade, Elements
from flightanalysis.criteria import *
from typing import Union



class NoseDrop(El):
    """A nose drop is used for spin entries. It consists of a loop to a vertical downline, with an integrated
    pitch rotation in the opposite direction to the loops pitch rotation so that the body axis finishes at
    break_angle off the vertical line"""
    parameters = El.parameters + "radius,break_angle,turn_angle,".split(",")
    def __init__(self, speed: float, radius: float, break_angle: float, turn_angle: float, uid: str=None):
        super().__init__(uid, speed)
        self.radius=radius
        self.break_angle = break_angle
        self.turn_angle = turn_angle

    def to_dict(self):
        return dict(
            kind = self.__class__.__name__,
            radius = self.radius,
            break_angle = self.break_angle,
            turn_angle = self.turn_angle,
            speed = self.speed,
            uid = self.uid
        )

    def create_template(self, istate: State, flown: State=None):
        
        _inverted = 1 if istate.transform.rotation.is_inverted()[0] else -1
        
        alpha =  np.arctan(istate.vel.z / istate.vel.x)[0]

        loop = Loop(self.speed, self.radius, 0.5*np.pi*_inverted).create_template(
            istate, flown
        ).superimpose_rotation(
            PY(), 
            -alpha -abs(self.break_angle) * _inverted
        ) 

        t0 = loop.time.t - loop.time.t[0]

        angles = PZ(self.turn_angle) * t0 / t0[-1]

        return loop.superimpose_angles(angles,"world").label(element=self.uid)
    
    def match_intention(self, transform: Transformation, flown: State):
        pass