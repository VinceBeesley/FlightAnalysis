import numpy as np
from geometry import Transformation, Coord, Point, Quaternion, PX, PY, PZ
from flightanalysis.state import State
from flightanalysis.base.table import Time
from scipy import optimize

from . import El

class Loop(El):

    def __init__(self, speed: float, diameter: float, angle: float, roll:float=0.0, ke: bool = False, uid: int=None):
        super().__init__(uid, speed)
        assert not diameter == 0 and not angle == 0
        self.angle = angle
        self.diameter = diameter
        self.roll = roll
        self.ke = ke
    
    @property
    def radius(self):
        return self.diameter / 2

    def scale(self, factor):
        return self.set_parms(diameter=self.diameter * factor)

    def create_template(self, transform: Transformation) -> State:
        """generate a template loop State 

        Args:
            transform (Transformation): initial pos and attitude

        Returns:
            [State]: flight data representing the loop
        """

        duration = 0.5 * self.diameter * abs(self.angle) / self.speed
        axis_rate = self.angle / duration
        
        if axis_rate == 0:
            raise NotImplementedError()

        state = State.from_transform(
            transform, 
            vel=PX(self.speed),
            rvel=PZ(self.angle / duration) if self.ke else PY(self.angle / duration) 
        ).extrapolate(duration)

        return self._add_rolls(state, self.roll)

    def match_axis_rate(self, pitch_rate: float):
        return self.set_parms(diameter=2 * self.speed / pitch_rate)

    def match_intention(self, transform: Transformation, flown: State):
        
        pos = Transformation(-transform.translation, transform.rotation.inverse()).point(flown.pos)

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
            roll=np.sign(flown.rvel.mean().x) * abs(self.roll)
        )
    

    def segment(self, transform:Transformation, flown: State, partitions=10):
        subsections = flown.segment(partitions)
        elms = [ self.match_intention( transform,sec) for sec in subsections ]
        
        return subsections, elms


def KELoop(*args, **kwargs):
    return Loop(*args, ke=True, **kwargs)
    
