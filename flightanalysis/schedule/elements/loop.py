import numpy as np
from geometry import Transformation, Coord, Point, Quaternion, PY
from flightanalysis.state import State
from flightanalysis.base.table import Time
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
        return self.set_parms(diameter=self.diameter * factor)

    def create_template(self, transform: Transformation, speed: float, simple=False) -> State:
        """generate a loop, based on intitial position, speed, amount of loop, radius. 

        Args:
            transform (Transformation): initial position
            speed (float): forward speed
            proportion (float): amount of loop. +ve offsets centre of loop in +ve body y or z
            r (float): radius of the loop (must be +ve)
            ke (bool, optional): [description]. Defaults to False. whether its a KE loop or normal

        Returns:
            [type]: [description]
        """

        duration = np.pi * self.diameter * abs(self.loops) / speed
        axis_rate = -self.loops * 2 * np.pi / duration
        freq = 1.0 if simple else State._construct_freq
        t = np.linspace(0, duration, max(int(duration * freq), 3))

        # TODO There must be a more elegant way to do this.
        if axis_rate == 0:
            raise NotImplementedError()
        radius = speed / axis_rate
        if not self.ke:
            radcoord = Coord.from_xy(
                transform.point(Point(0, 0, -radius)),
                transform.rotate(Point(0, 0, 1)),
                transform.rotate(Point(1, 0, 0))
            )
            angles = PY(axis_rate).tile(len(t)) * t

            radcoordpoints = Point(radius, radius, 0) * \
                Point(np.cos(angles.y), np.sin(angles.y), np.zeros(len(angles)))

            
        else:
            radcoord = Coord.from_xy(
                transform.point(Point(0, -radius, 0)),
                transform.rotate(Point(0, 1, 0)),
                transform.rotate(Point(1, 0, 0))
            )
            angles = Point.from_point(Point(0, 0, -axis_rate), len(t)) * t

            radcoordpoints = Point(radius, radius, 0) * \
                Point(np.cos(-angles.z), np.sin(-angles.z), np.zeros(len(angles)))

        pos=Transformation.from_coords(Coord.from_nothing(), radcoord).point(radcoordpoints)
        att = Quaternion.full(transform.rotation, len(t)).body_rotate(angles)

        el = State.from_constructs(Time.from_t(t), pos, att)
        return self._add_rolls(el, self.rolls)

    def match_axis_rate(self, pitch_rate: float, speed: float):
        return self.set_parms(diameter=2 * speed / pitch_rate)

    def match_intention(self, transform: Transformation, flown: State):
        # https://scipy-cookbook.readthedocs.io/items/Least_Squares_Circle.html
        pos = transform.point(flown.pos)

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

        return self.set_parms(
            diameter=2 * calc_R(*center).mean(),
            rolls=np.sign(flown.rvel.mean().x) * abs(self.rolls)
        )
    

    def segment(self, transform:Transformation, flown: State, partitions=10):
        subsections = flown.segment(partitions)
        elms = [ self.match_intention( transform,sec) for sec in subsections ]
        
        return subsections, elms
