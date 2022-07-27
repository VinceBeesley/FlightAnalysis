
import numpy as np
from geometry import Transformation, Point, PX
from flightanalysis.base.table import Time
from flightanalysis.state import State
from enum import Enum
from . import El


class Line(El):
    def __init__(self, speed, length, roll=0, uid:int=None):
        super().__init__(uid, speed)
        self.length = length
        self.roll = roll
        
    def scale(self, factor):
        return self.set_parms(length=self.length * factor)

    @property
    def rate(self):
        return abs(self.roll) * self.speed / self.length

    @property
    def roll_direction(self):
        return np.sign(self.roll)

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
        length = abs(
            (flown[-1].pos - flown[0].pos).scalar_projection(
                transform.rotate(PX())
            )[0]
        )
        return self.set_parms(
            length=length,
            roll=np.sign(np.mean(flown.rvel.x)) * abs(self.roll),
            speed=np.mean(flown.u)
        )

    @staticmethod
    def from_roll(speed: float, rate: float, angle: float):
        return Line(speed, rate * angle * speed, angle )

def lineid(uid: int, speed: float, length: float, roll:float=0):
    return Line(speed, length, roll, uid)
    