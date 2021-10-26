import numpy as np
from geometry import Transformation, Points, scalar_projection
from flightanalysis import Section
from scipy import optimize

from . import El

class Loop(El):
    def __init__(self, diameter: float, loops: float, rolls=0.0, ke: bool = False, r_tag=True, uid: str = None):
        super().__init__(uid)
        assert not diameter == 0 and not loops == 0

        self.loops = loops
        self.diameter = diameter
        self.rolls = rolls
        self.ke = ke
        self.r_tag = r_tag

    def scale(self, factor):
        return self.set_parameter(diameter=self.diameter * factor)

    def create_template(self, transform: Transformation, speed: float, simple=False):
        el = Section.from_loop(transform, speed, self.loops,
                               0.5 * self.diameter, self.ke, freq=1.0 if simple else None)
        return self._add_rolls(el, self.rolls)

    def match_axis_rate(self, pitch_rate: float, speed: float):
        return self.set_parameter(diameter=2 * speed / pitch_rate)

    def match_intention(self, transform: Transformation, flown: Section):
        # https://scipy-cookbook.readthedocs.io/items/Least_Squares_Circle.html
        pos = transform.point(Points.from_pandas(flown.pos))

        if self.ke:
            x, y = pos.x, pos.y
        else:
            x, y = pos.x, pos.z

        # TODO this does not constrain the starting point
        def calc_R(xc, yc): return np.sqrt((x-xc)**2 + (y-yc)**2)

        def f_2(c):
            Ri = calc_R(*c)
            return Ri - Ri.mean()

        center, ier = optimize.leastsq(f_2, (np.mean(x), np.mean(y)))

        return self.set_parameter(
            diameter=2 * calc_R(*center).mean(),
            rolls=np.sign(np.mean(Points.from_pandas(
                flown.brvel).x)) * abs(self.rolls)
        )

    def set_parameter(self, diameter=None, loops=None, rolls=None, ke=None, r_tag=None):
        return Loop(
            diameter if not diameter is None else self.diameter,
            loops if not loops is None else self.loops,
            rolls if not rolls is None else self.rolls,
            ke if not ke is None else self.ke,
            r_tag if not r_tag is None else self.r_tag,
            self.uid
        )

    def segment(self, transform:Transformation, flown: Section, partitions=10):
        subsections = flown.segment(partitions)
        elms = [ self.match_intention( transform,sec) for sec in subsections ]
        
        return subsections, elms
