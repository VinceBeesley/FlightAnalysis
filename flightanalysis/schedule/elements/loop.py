import numpy as np
import pandas as pd
from geometry import Transformation, Coord, Point, Quaternion, PX, PY, PZ
from flightanalysis.state import State
from flightanalysis.base.table import Time
from scipy import optimize
from flightanalysis.criteria import (
    Continuous, ContinuousResult, intra_f3a_angle, intra_f3a_radius, intra_f3a_speed
)
from flightanalysis.criteria import Results
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

    def corresponding_template(self, itrans: Transformation, aligned: State):
        c = self.centre(itrans)

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

    def coord(self, itrans: Transformation) -> Coord:
        """Create the loop coordinate frame
        origin on loop centre,
        X axis towards start of radius,
        Z axis normal"""
        centre =self.centre(itrans)   

        loop_normal_vector = itrans.att.inverse().transform_point(
            self.normal_direction
        )

        return Coord.from_zx(centre, loop_normal_vector, itrans.pos - centre)


    def measure_radial_position(self, flown:State):
        """The radial position in radians given a state in the loop coordinate frame"""
        return np.arctan2(flown.pos.y, flown.pos.x)

    def measure_radius(self, flown:State):
        """The radius in m given a state in the loop coordinate frame"""
        return abs(flown.pos * Point(1,1,0))

    def measure_track(self, flown: State):
        """The track in radians (lateral direction error) given a state in the loop coordinate frame"""
        lc_vels = flown.att.transform_point(flown.vel) 
        return np.arcsin(lc_vels.z/abs(lc_vels) )

    def measure_roll_angle(self, flown: State):
        """The roll error given a state in the loop coordinate frame"""
        roll_vector = flown.att.inverse().transform_point(PZ(1))
        return np.arctan2(roll_vector.z, roll_vector.y)

    def setup_analysis_state(self, flown: State, template:State):
        """Change the reference coordinate frame for a flown loop element to the
        loop coord"""   
        return flown.move_back(Transformation.from_coord(self.coord(
            Transformation(flown.pos[0], template.att[0])
        )))


    def score(self, flown: State):
        radpos = self.measure_radial_position(flown)
        ms = lambda data: pd.Series(data, index=radpos)
        return Results([
            intra_f3a_radius("radius", ms(self.measure_radius(flown))),
            intra_f3a_angle("roll_angle", ms(self.measure_roll_angle(flown))),
            intra_f3a_angle("track", ms(self.measure_track(flown))),
            intra_f3a_speed("speed", ms(abs(flown.vel))),
            #intra_f3a_angle("exit", lookup(np.degrees())
        ])

    def match_axis_rate(self, pitch_rate: float):
        return self.set_parms(radius=self.speed / pitch_rate)


    def match_intention(self, itrans: Transformation, flown: State):      
        jit = flown.judging_itrans(itrans)
        pos = jit.att.transform_point(flown.pos - jit.pos)

        if self.ke:
            x, y = pos.x, pos.y
        else:
            x, y = pos.x, pos.z
            
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
    

