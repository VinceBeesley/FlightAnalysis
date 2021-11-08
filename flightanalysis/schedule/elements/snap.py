import numpy as np
from geometry import Transformation, Quaternion, Point
from flightanalysis import Section, State
    
from . import El, Line


#TODO default rate is set for box size of 2m, this is misleading. When scaled to 170m distance it is about right.
class Snap(El):
    def __init__(self, rolls: float, negative=False, rate:float=3400,l_tag=True, uid: str = None):
        super().__init__(uid)
        self.rolls = rolls
        self.negative = negative
        self.l_tag = l_tag
        self.rate = rate

    def scale(self, factor):
        return self.set_parms(rate=self.rate/factor)

    def create_template(self, transform: Transformation, speed: float, simple: bool = False) -> Section: 
        """Generate a section representing a snap roll, this is compared to a real snap in examples/snap_rolls.ipynb"""
        freq = 1.0 if simple else Section._construct_freq

        direc = -1 if self.negative else 1
        break_angle = np.radians(10)

        pitch_rate = self.rate
        
        pitch_break = Section.extrapolate_state(
            State.from_transform(transform, bvel=Point(speed, 0, 0)), 
            2 * np.pi * break_angle / pitch_rate, freq=freq
        ).superimpose_rotation(Point(0, 1, 0), direc * break_angle )
        
        
        body_autorotation_axis = Quaternion.from_euler(
            Point(0, direc * break_angle, 0)
        ).inverse().transform_point(Point(1,0,0))
        
        autorotation = Section.extrapolate_state(
            pitch_break[-1], 2 * np.pi * abs(self.rolls) / self.rate, freq=freq
        ).superimpose_rotation(body_autorotation_axis, 2 * np.pi * self.rolls)

        correction = Section.extrapolate_state(
            autorotation[-1], 
            2 * np.pi * break_angle / pitch_rate, freq=freq
        ).superimpose_rotation(Point(0, 1, 0), -direc * break_angle )

        return self._add_rolls(Section.stack([
            pitch_break.label(sub_element="pitch_break"), 
            autorotation.label(sub_element="autorotation"), 
            correction.label(sub_element="correction")
            ]), 0)

    def match_axis_rate(self, snap_rate: float, speed: float):
        return self.set_parms()  # TODO should probably allow this somehow

    def match_intention(self, transform: Transformation, flown: Section):
        #TODO need to match flown pos/neg if F3A, not if IMAC
        return self.set_parms(
            rolls=np.sign(np.mean(flown.gbrvel.x)) * abs(self.rolls)
        )

    @property
    def length(self):
        return self.create_template(Transformation(), 30.0, True).get_state_from_index(-1).pos.x