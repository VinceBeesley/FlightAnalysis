from __future__ import annotations
import numpy as np
from geometry import Transformation, Coord, Point, PX, PY, PZ

from flightanalysis.state import State
from flightanalysis.base.table import Time
from flightanalysis.schedule.scoring import *
from . import Element


class Loop(Element):
    parameters = Element.parameters + "radius,angle,roll,ke,rate".split(",")

    def __init__(self, speed: float, radius: float, angle: float, roll:float=0.0, ke: bool = False, uid: str=None):
        super().__init__(uid, speed)
        assert not radius == 0 and not angle == 0
        self.angle = angle
        self.radius = radius   
        self.roll = roll
        self.ke = ke

    @property
    def intra_scoring(self) -> DownGrades:
        _intra_scoring = DownGrades([
            DownGrade(Measurement.speed, f3a.intra_speed),
            DownGrade(Measurement.radius, f3a.intra_radius),
            DownGrade(Measurement.track_y, f3a.intra_track),
            DownGrade(Measurement.track_z, f3a.single_track),
        ])
        if not self.roll == 0:
            _intra_scoring.add(DownGrade(Measurement.roll_rate, f3a.intra_roll_rate))
            _intra_scoring.add(DownGrade(Measurement.roll_angle, f3a.single_roll))
        else:
            _intra_scoring.add(DownGrade(Measurement.roll_angle, f3a.intra_roll))
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

    def create_template(self, istate: State, time: Time=None) -> State:
        """Generate a template loop. 

        Args:
            istate (State): initial state

        Returns:
            [State]: flight data representing the loop
        """
        duration = self.radius * abs(self.angle) / self.speed
        
        if self.angle == 0:
            raise NotImplementedError()      
        
        v = PX(self.speed) if istate.vel == 0 else istate.vel.scale(self.speed)
        
        return self._add_rolls(
            istate.copy(
                vel=v,
                rvel=PZ(self.angle / duration) if self.ke else PY(self.angle / duration)
            ).fill(
                Element.create_time(duration, time)
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

    def coord_old(self, template: State) -> Coord:
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

    def measure_radial_position(self, flown:State, template:State, coord: Coord):
        """The radial position in radians given a state in the loop coordinate frame"""
        return np.arctan2(flown.pos.y, flown.pos.x)

    def measure_ratio(self, flown: State, template:State, coord: Coord):
        rpos = self.measure_radial_position(flown, template, coord)
        return rpos / rpos[-1]

    def measure_radius_coord(self, flown:State, template:State, coord: Coord):
        """The radius in m given a state in the loop coordinate frame"""
        return abs(flown.pos * Point(1,1,0))

    def measure_radius(self, flown:State, template:State, coord: Coord):
        """The radius vector in m given a state in the loop coordinate frame"""
        centre = flown.att.transform_point(flown.arc_centre())

        if self.ke:
            centre = centre * Point(1,1,0)
        else:
            centre = centre * Point(1,0,1)
        return abs(centre)

    def measure_end_angle(self, flown: State, template:State, coord: Coord):
        template_vels = template.att.transform_point(template.vel) * Point(1,1,0)
        flown_vels = flown.att.transform_point(flown.vel) * Point(1,1,0)
        return Point.angle_between(template_vels[-1], flown_vels[-1])

    def match_axis_rate(self, pitch_rate: float) -> Loop:
        return self.set_parms(radius=self.speed / pitch_rate)

    def match_intention(self, itrans: Transformation, flown: State) -> Loop:
        return self.set_parms(
            radius = self.measure_radius(flown, None, None).mean(),
            roll=abs(self.roll) * np.sign(np.mean(flown.rvel.x)),
            angle=abs(self.angle) * np.sign(flown.r.mean() if self.ke else flown.q.mean()),
            speed=abs(flown.vel).mean()
        )

    def match_intention_fit(self, itrans: Transformation, flown: State) -> Loop:
        from scipy import optimize
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
            angle=abs(self.angle) * np.sign(flown.r.mean() if self.ke else flown.q.mean()),
            speed=abs(flown.vel).mean()
        )
    

    def segment(self, transform:Transformation, flown: State, partitions=10):
        subsections = flown.segment(partitions)
        elms = [ self.match_intention( transform,sec) for sec in subsections ]
        
        return subsections, elms

    def copy_direction(self, other) -> Loop:
        return self.set_parms(
            roll=abs(self.roll) * np.sign(other.roll),
            angle=abs(self.angle) * np.sign(other.angle)
        )




def KELoop(*args, **kwargs):
    return Loop(*args, ke=True, **kwargs)
    

