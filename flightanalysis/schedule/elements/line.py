
import numpy as np
from geometry import Transformation, Point, scalar_projection, Points, scalar_projection
from flightanalysis import Section

from . import El


class Line(El):
    def __init__(self, length, rolls=0, l_tag=True, uid: str = None):
        super().__init__(uid)
        self.length = length
        self.rolls = rolls
        self.l_tag = l_tag

    def set_parameter(self, length=None, rolls=None, l_tag=None):
        return Line(
            length if length is not None else self.length,
            rolls if rolls is not None else self.rolls,
            l_tag if l_tag is not None else self.l_tag,
            self.uid
        )

    def scale(self, factor):
        return self.set_parameter(length=self.length * factor)

    def create_template(self, transform: Transformation, speed: float, simple: bool = False):
        el = Section.from_line(
            transform, speed, self.length, freq=1.0 if simple else None)
        return self._add_rolls(el, self.rolls)

    def match_axis_rate(self, roll_rate: float, speed: float):
        # roll rate in radians per second, speed in m / s
        if not self.rolls == 0.0:
            return self.set_parameter(
                length=2 * np.pi * abs(self.rolls) * speed / roll_rate)
        else:
            return self.set_parameter()

    def match_intention(self, transform: Transformation, flown: Section):
        length = abs(scalar_projection(
            flown.get_state_from_index(-1).pos -
            flown.get_state_from_index(0).pos,
            transform.rotate(Point(1, 0, 0))
        ))
        return self.set_parameter(
            length=length,
            rolls=np.sign(np.mean(Points.from_pandas(flown.brvel).x)) *
            abs(self.rolls)
        )