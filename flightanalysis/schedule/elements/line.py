
import numpy as np
from geometry import Transformation, Point, scalar_projection, Points, Quaternions
from flightanalysis import Section, State

from . import El


class Line(El):
    def __init__(self, length, rolls=0, l_tag=True, uid: str = None):
        super().__init__(uid)
        self.length = length
        self.rolls = rolls
        self.l_tag = l_tag


    def scale(self, factor):
        return self.set_parms(length=self.length * factor)

    def create_template(self, transform: Transformation, speed: float, simple: bool = False) -> Section:
        """contstruct a Section representing the judging frame for this line element

        Args:
            transform (Transformation): initial position and orientation
            speed (float): speed in judging frame X axis
            simple (bool, optional): just create the first and last points of the section. Defaults to False.

        Returns:
            Section: [description]
        """
        sec= Section.extrapolate_state(
            State.from_transform(
                transform, 
                bvel=Point(speed, 0.0, 0.0)
            ), 
            duration=self.length / speed, 
            freq=1.0 if simple else None
        )

        return self._add_rolls(sec, self.rolls)

    def match_axis_rate(self, roll_rate: float, speed: float):
        # roll rate in radians per second, speed in m / s
        if not self.rolls == 0.0:
            return self.set_parms(
                length=2 * np.pi * abs(self.rolls) * speed / roll_rate)
        else:
            return self.set_parms()

    def match_intention(self, transform: Transformation, flown: Section):
        length = abs(scalar_projection(
            flown.get_state_from_index(-1).pos -
            flown.get_state_from_index(0).pos,
            transform.rotate(Point(1, 0, 0))
        ))
        return self.set_parms(
            length=length,
            rolls=np.sign(np.mean(Point(flown.brvel).x)) * abs(self.rolls)
        )



