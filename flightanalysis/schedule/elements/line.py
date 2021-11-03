
import numpy as np
from geometry import Transformation, Point, scalar_projection, Points, Quaternions
from flightanalysis import Section

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
        """generate a section representing a line. Provide an initial rotation rate to represent a roll.

        Args:
            initial (State): The initial state, the line will be drawn in the direction
                            of the initial velocity vector.
            t (np.array): the timesteps to create states for
        Returns:
            Section: Section class representing the line or roll.
        """
        t = Section.t_array(duration=self.length / speed, freq=1.0 if simple else None)
        ibvel = Point(speed, 0.0, 0.0)
        bvel = Points.from_point(ibvel, len(t))

        pos = Points.from_point(transform.translation,len(t)) + transform.rotate(bvel) * t

        att = Quaternions.from_quaternion(transform.rotation, len(t))

        sec = Section.from_constructs(
            t, pos, att, bvel,
            Points(np.zeros((len(t), 3))),
            Points(np.zeros((len(t), 3)))
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
            rolls=np.sign(np.mean(Points.from_pandas(flown.brvel).x)) * abs(self.rolls)
        )



