import numpy as np
from geometry import Transformation, Quaternion, Point, Euler, PX, PY, PZ, P0
from flightanalysis.state import State
from flightanalysis.base.table import Time
from . import El, Line


#TODO default rate is set for box size of 2m, this is misleading. When scaled to 170m distance it is about right.
class Snap(El):
    def __init__(self, speed:float, rolls: float, negative=False, rate:float=3400, uid: int=None):
        super().__init__(uid, speed)
        self.rolls = rolls
        self.negative = negative
        self.rate = rate

    def scale(self, factor):
        return self.set_parms(rate=self.rate/factor)

    def create_template(self, transform: Transformation) -> State: 
        """Generate a section representing a snap roll, this is compared to a real snap in examples/snap_rolls.ipynb"""
        
        direc = -1 if self.negative else 1
        break_angle = np.radians(10)

        pitch_rate = self.rate
        
        pitch_break = State.from_transform(
            transform, 
            time = Time(0, 1/State._construct_freq),
            vel=PX(self.speed)
        ).extrapolate( 
            2 * np.pi * break_angle / pitch_rate
        ).superimpose_rotation(PY(), direc * break_angle)
        
        
        body_autorotation_axis = Euler(0, direc * break_angle, 0).inverse().transform_point(PX())
        
        autorotation = pitch_break[-1].copy(rvel=P0()).extrapolate(
            2 * np.pi * abs(self.rolls) / self.rate
        ).superimpose_rotation(
            body_autorotation_axis, 
            2 * np.pi * self.rolls,
        )

        correction = autorotation[-1].copy(rvel=P0()).extrapolate( 
            2 * np.pi * break_angle / pitch_rate
        ).superimpose_rotation(PY(), -direc * break_angle )

        return self._add_rolls(
            State.stack([
                pitch_break.label(sub_element="pitch_break"), 
                autorotation.label(sub_element="autorotation"), 
                correction.label(sub_element="correction")
            ]), 
            0
        )

    def match_axis_rate(self, snap_rate: float):
        return self.set_parms()  # TODO should probably allow this somehow

    def match_intention(self, transform: Transformation, flown: State):
        #TODO need to match flown pos/neg if F3A, not if IMAC
        return self.set_parms(
            rolls=np.sign(flown.rvel.mean().x)[0] * abs(self.rolls)
        )

    @property
    def length(self):
        return self.create_template(Transformation(), 30.0)[-1].pos.x[0]