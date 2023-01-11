import numpy as np
import pandas as pd
from geometry import Transformation, Coord, Point, Quaternion, PX, PY, PZ
from flightanalysis.state import State
from flightanalysis.base.table import Time
from scipy import optimize
from flightanalysis.criteria import *
from . import El, DownGrades, DownGrade
from typing import Union

class Loop(El):
    parameters = El.parameters + "radius,angle,roll,ke,rate".split(",")

    def __init__(self, speed: float, radius: float, angle: float, roll:float=0.0, ke: bool = False, uid: str=None):
        super().__init__(uid, speed)
        assert not radius == 0 and not angle == 0
        self.angle = angle
        self.radius = radius   
        self.roll = roll
        self.ke = ke

    @property
    def intra_scoring(self):

        _intra_scoring = DownGrades([
            DownGrade("speed", "measure_speed", intra_f3a_speed),
            DownGrade("radius", "measure_radius", intra_f3a_radius),
            DownGrade("track", "measure_ip_track", intra_f3a_angle),
            DownGrade("loop_amount", "measure_end_angle", basic_angle_f3a),
        ])

        if not self.roll == 0:
            _intra_scoring.add(DownGrade("roll_rate", "measure_roll_rate", intra_f3a_roll_rate))
            _intra_scoring.add(DownGrade("roll_amount", "measure_end_roll_angle", basic_angle_f3a))
        else:
            _intra_scoring.add(DownGrade("roll_angle", "measure_roll_angle_error", intra_f3a_angle))
        return _intra_scoring

    def describe(self):
        d1 = "loop" if self.roll==0 else f"rolling loop"
        return f"{d1}, radius = {self.radius} m, rolls = {self.roll}"

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

    def create_template(self, istate: Union[State, Transformation], flown: State=None) -> State:
        """Generate a template loop. 

        Args:
            istate (Transformation): initial pos and attitude, or State

        Returns:
            [State]: flight data representing the loop
        """
        duration = self.radius * abs(self.angle) / self.speed
        
        if self.angle == 0:
            raise NotImplementedError()      
                
        return self._add_rolls(
            self._create_istate(istate, self.speed).copy(
                rvel=PZ(self.angle / duration) if self.ke else PY(self.angle / duration)
            ).fill(
                El.create_time(duration, flown)
            ), 
            self.roll
        )

    @property
    def centre_vector(self) -> Point:
        """Return the body frame vector from the start of the loop to the centre"""
        cv= PY if self.ke else PZ
        return cv(self.radius * np.sign(self.angle))

    @property
    def normal_direction(self) -> Point:
        """Return the loop normal direction vector in the loop coord. The model moves around this
        in the positive direction (right handed screw rule)."""
        nd = PZ if self.ke else PY
        return nd(np.sign(self.angle))

    def centre(self, itrans: Transformation) -> Point:
        """return the position of the centre of the loop given the transformation
        to the first State in the loop"""
        return itrans.pos - itrans.att.transform_point(self.centre_vector)

    def coord(self, template: State) -> Coord:
        """Create the loop coordinate frame. Assumes inital position is in the same as flown
        origin on loop centre,
        X axis towards start of radius,
        Z axis normal"""
        itrans = template[0].transform
        centre =self.centre(itrans)   

        loop_normal_vector = itrans.att.transform_point(
            self.normal_direction
        )

        return Coord.from_zx(centre, loop_normal_vector, itrans.pos - centre)

    def measure_radial_position(self, flown:State, template:State):
        """The radial position in radians given a state in the loop coordinate frame"""
        return np.arctan2(flown.pos.y, flown.pos.x)

    def measure_ratio(self, flown: State, template:State):
        rpos = self.measure_radial_position(flown, template)
        return rpos / rpos[-1]

    def measure_radius(self, flown:State, template:State):
        """The radius in m given a state in the loop coordinate frame"""
        return abs(flown.pos * Point(1,1,0))
   
    def measure_end_angle(self, flown: State, template:State):
        template_vels = template.att.transform_point(template.vel) * Point(1,1,0)
        flown_vels = flown.att.transform_point(flown.vel) * Point(1,1,0)
        return Point.angle_between(template_vels[-1], flown_vels[-1])

    def match_axis_rate(self, pitch_rate: float):
        return self.set_parms(radius=self.speed / pitch_rate)

    def match_intention(self, itrans: Transformation, flown: State):
        jit = flown.judging_itrans(itrans)
        pos = jit.att.transform_point(flown.pos - jit.pos)

        x, y = (pos.x, pos.y) if self.ke else (pos.x, pos.z)
            
        calc_R = lambda x, y, xc, yc: np.sqrt((x-xc)**2 + (y-yc)**2)

        def f_2(c):
            return calc_R(x, y, *c) - calc_R(x[0], y[0], *c)

        center, ier = optimize.leastsq(f_2, (np.mean(x), np.mean(y)))

        return self.set_parms(
            radius=calc_R(x[0], y[0],*center).mean(),
            roll=abs(self.roll) * np.sign(np.mean(flown.rvel.x)),
            angle=abs(self.angle) * np.sign(np.sign(np.mean(flown.rvel.y))),
            speed=np.mean(flown.u)
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
    

