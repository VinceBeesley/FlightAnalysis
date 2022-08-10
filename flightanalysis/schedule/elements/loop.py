import numpy as np
from geometry import Transformation, Coord, Point, Quaternion, PX, PY, PZ
from flightanalysis.state import State
from flightanalysis.base.table import Time
from scipy import optimize

from . import El

class Loop(El):
    parameters = El.parameters + "radius,angle,roll,ke,rate".split(",")
    def __init__(self, speed: float, radius: float, angle: float, roll:float=0.0, ke: bool = False, uid: str=None):
        super().__init__(uid, speed)
        assert not radius == 0 and not angle == 0
        self.angle = angle
        self.radius = radius   
        self.roll = roll
        self.ke = ke

    def to_dict(self):
        return dict(
            kind=self.__class__.__name__,
            angle=self.angle,
            radius=self.radius,
            roll=self.roll,
            speed=self.speed,
            ke=self.ke,
            uid=self.uid
        )

    @property
    def diameter(self):
        return self.radius * 2

    @property
    def rate(self):
        return self.roll * self.speed / (self.angle * self.radius)

    def create_template(self, transform: Transformation) -> State:
        """generate a template loop State 

        Args:
            transform (Transformation): initial pos and attitude

        Returns:
            [State]: flight data representing the loop
        """

        duration = self.radius * abs(self.angle) / self.speed
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
        return self.set_parms(radius=self.speed / pitch_rate)

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
            radius=calc_R(*center).mean(),
            roll=np.sign(flown.rvel.mean().x[0]) * abs(self.roll)
        )
    

    def segment(self, transform:Transformation, flown: State, partitions=10):
        subsections = flown.segment(partitions)
        elms = [ self.match_intention( transform,sec) for sec in subsections ]
        
        return subsections, elms

    def copy_direction(self, other):
        return self.set_parms(
            roll=abs(self.roll) * np.sign(other.roll),
            angle=abs(self.angle) * np.sign(other.angle)
        )

def KELoop(*args, **kwargs):
    return Loop(*args, ke=True, **kwargs)
    
