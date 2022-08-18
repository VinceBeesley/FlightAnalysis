
import numpy as np
from geometry import Transformation, Point, PX
from flightanalysis.base.table import Time
from flightanalysis.state import State
from enum import Enum
from . import El


class Line(El):
    parameters = El.parameters + "length,roll,rate".split(",")
    def __init__(self, speed, length, roll=0, uid:str=None):
        super().__init__(uid, speed)
        self.length = length
        self.roll = roll
    
    def to_dict(self):
        return dict(
            kind=self.__class__.__name__,
            length=self.length,
            roll=self.roll,
            speed=self.speed,
            uid=self.uid
        )

    def scale(self, factor):
        return self.set_parms(length=self.length * factor)

    @property
    def rate(self):
        return abs(self.roll) * self.speed / self.length

    def create_template(self, transform: Transformation) -> State:
        """contstruct a State representing the judging frame for this line element

        Args:
            transform (Transformation): initial position and orientation
            speed (float): speed in judging frame X axis
            simple (bool, optional): just create the first and last points of the section. Defaults to False.

        Returns:
            State: [description]
        """
        sec= State.from_transform(
            transform, 
            time = Time(0, 1/State._construct_freq),
            vel=PX(self.speed)
        ).extrapolate(duration=self.length / self.speed)

        return self._add_rolls(sec, self.roll)

    def match_axis_rate(self, roll_rate: float):
        # roll rate in radians per second
        if not self.roll == 0.0:
            return self.set_parms(
                length=abs(self.roll) * self.speed / roll_rate)
        else:
            return self.set_parms()

    def match_intention(self, transform: Transformation, flown: State):
        jit = flown.judging_itrans(transform)
        return self.set_parms(
            length=jit.att.inverse().transform_point(flown.pos - jit.pos).x[-1],
            roll=np.sign(np.mean(flown.rvel.x)) * abs(self.roll),
            speed=np.mean(flown.u)
        )

    @staticmethod
    def from_roll(speed: float, rate: float, angle: float):
        return Line(speed, rate * angle * speed, angle )

    def copy_direction(self, other):
        return self.set_parms(roll=abs(self.roll) * np.sign(other.roll))

def lineid(uid: int, speed: float, length: float, roll:float=0):
    return Line(speed, length, roll, uid)
    