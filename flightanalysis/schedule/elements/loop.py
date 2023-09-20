from __future__ import annotations
import numpy as np
from geometry import Transformation, Coord, Point, PX, PY, PZ

from flightanalysis.state import State
from flightanalysis.base.table import Time
from flightanalysis.schedule.scoring.criteria.f3a_criteria import F3A
from flightanalysis.schedule.scoring import Measurement, DownGrade, DownGrades
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
            DownGrade(Measurement.speed, F3A.intra.speed),
            DownGrade(Measurement.radius, F3A.intra.radius),
            DownGrade(Measurement.track_y, F3A.intra.track),
            DownGrade(Measurement.track_z, F3A.single.track),
        ])
        if not self.roll == 0:
            _intra_scoring.add(DownGrade(Measurement.roll_rate, F3A.intra.roll_rate))
            _intra_scoring.add(DownGrade(Measurement.roll_angle, F3A.single.roll))
        else:
            _intra_scoring.add(DownGrade(Measurement.roll_angle, F3A.intra.roll))
        return _intra_scoring

    def describe(self):
        d1 = "loop" if self.roll==0 else f"rolling loop"
        return f"{d1}, radius = {self.radius} m, rolls = {self.roll}"

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

    def measure_radius(self, itrans: Transformation, flown:State):
        """The radius vector in m given a state in the loop coordinate frame"""
        centre = flown.arc_centre()

        wvec = itrans.att.transform_point(PZ() if self.ke else PY())
        bvec = flown.att.inverse().transform_point(wvec)
        return abs(Point.vector_rejection(centre, bvec))

    def weighted_average_radius(self, itrans: Transformation, flown: State) -> float:
        rads = self.measure_radius(itrans, flown)
        angles = np.arctan(abs(flown.vel) * flown.dt / rads)
        return np.sum(rads * angles) / np.sum(angles)

    def match_intention(self, itrans: Transformation, flown: State) -> Loop:
        rv = flown.rvel # .mean() if self.ke else flown.q.mean()
        wrv = flown.att.transform_point(rv)
        itrv = itrans.att.transform_point(wrv)

        return self.set_parms(
            radius = self.weighted_average_radius(itrans, flown),# self.measure_radius(itrans, flown).mean(),
            roll=abs(self.roll) * np.sign(np.mean(flown.rvel.x)),
            angle=abs(self.angle) * np.sign(itrv.z.mean() if self.ke else itrv.y.mean()),
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

    def radius_visibility(self, st: State):
        axial_dir = st[0].att.transform_point(PZ() if self.ke else PY())  
        return Measurement._rad_vis(st.pos.mean(), axial_dir)


def KELoop(*args, **kwargs):
    return Loop(*args, ke=True, **kwargs)
    

