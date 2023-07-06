from __future__ import annotations
import numpy as np
from geometry import Transformation, P0, PX, PY, PZ
from flightanalysis.base.table import Time
from flightanalysis.state import State

from .element import Element
from flightanalysis.schedule.scoring import *


class Line(Element):
    parameters = Element.parameters + "length,roll,rate".split(",")

    def __init__(self, speed, length, roll=0, uid:str=None):
        super().__init__(uid, speed)
#        if length < 0:
 #           raise ValueError("Cannot create line with negative length")
        self.length = length
        self.roll = roll
    
    @property
    def intra_scoring(self) -> DownGrades:
        _intra_scoring = DownGrades([
            DownGrade(Measurement.speed, f3a.intra_speed),
            DownGrade(Measurement.track_y, f3a.intra_track),
            DownGrade(Measurement.track_z, f3a.intra_track)
        ])

        if not self.roll == 0:
            _intra_scoring.add(DownGrade(Measurement.roll_rate, f3a.intra_roll_rate))
            _intra_scoring.add(DownGrade(Measurement.roll_angle, f3a.single_roll))
        else:
            
            _intra_scoring.add(DownGrade(Measurement.roll_angle, f3a.intra_roll))
        return _intra_scoring



    def describe(self):
        d1 = "line" if self.roll==0 else f"{self.roll} roll"
        return f"{d1}, length = {self.length} m"

    def to_dict(self):
        return dict(
            kind=self.__class__.__name__,
            length=self.length,
            roll=self.roll,
            speed=self.speed,
            uid=self.uid
        )

    @property
    def rate(self):
        return self.roll * self.speed / self.length

    def create_template(self, istate: State, time: Time=None) -> State:
        """construct a State representing the judging frame for this line element

        Args:
            istate (Transformation): initial position and orientation
            speed (float): speed in judging frame X axis
            simple (bool, optional): just create the first and last points of the section. Defaults to False.

        Returns:
            State: [description]
        """
        v = PX(self.speed) if istate.vel == 0 else istate.vel.scale(self.speed)
             
        return self._add_rolls(
            istate.copy(vel=v, rvel=P0()).fill(
                Element.create_time(self.length / self.speed, time)
            ), 
            self.roll
        )

    def match_axis_rate(self, roll_rate: float) -> Line:
        # roll rate in radians per second
        if not self.roll == 0.0:
            return self.set_parms(
                length=abs(self.roll) * self.speed / roll_rate)
        else:
            return self.set_parms()

    def match_intention(self, transform: Transformation, flown: State) -> Line:
        jit = flown.judging_itrans(transform)
        return self.set_parms(
            length=jit.att.inverse().transform_point(flown.pos - jit.pos).x[-1],
            roll=np.sign(np.mean(flown.p)) * abs(self.roll),
            speed=abs(flown.vel).mean()
        )

    @staticmethod
    def from_roll(speed: float, rate: float, angle: float) -> Line:
        return Line(speed, rate * angle * speed, angle )

    def copy_direction(self, other) -> Line:
        return self.set_parms(roll=abs(self.roll) * np.sign(other.roll))
