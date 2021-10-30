import numpy as np
from geometry import Transformation, Quaternion, Point
from flightanalysis import Section
    
from . import El



class Snap(El):
    def __init__(self, rolls: float, negative=False, l_tag=True, uid: str = None):
        super().__init__(uid)
        self.rolls = rolls
        self.negative = negative
        self.l_tag = l_tag

    def set_parameter(self, rolls=None, negative=None, l_tag=None):
        return Snap(
            rolls if rolls is not None else self.rolls,
            negative if negative is not None else self.negative,
            l_tag if l_tag is not None else self.l_tag,
            self.uid
        )

    def scale(self, factor):
        return self.set_parameter()

    def create_template(self, transform: Transformation, speed: float, simple: bool = False): 
        """Generate a section representing a snap roll, this is compared to a real snap in examples/snap_rolls.ipynb"""
        freq = 1.0 if simple else Section._construct_freq

        direc = -1 if self.negative else 1
        break_angle = np.radians(20)
        break_amount = direc * break_angle / (2 * np.pi)
        body_autorotation_axis = Quaternion.from_euler(
            Point(0, direc * break_angle, 0)
        ).inverse().transform_point(Point(1,0,0))

        pitch_break = Section.from_line(
            transform, speed, speed/5, freq=freq
        ).superimpose_rotation(Point(0, 1, 0), break_amount )
        
        autorotation = Section.extrapolate_state(
            pitch_break.get_state_from_index(-1), speed * abs(self.rolls) / 50, freq=freq
        ).superimpose_rotation(body_autorotation_axis, self.rolls)

        correction = Section.extrapolate_state(
            autorotation.get_state_from_index(-1), 
            speed/300, freq=freq
        ).superimpose_rotation(Point(0, 1, 0), -break_amount )

        pitch_break.data["sub_element"] = "pitch_break"
        autorotation.data["sub_element"] = "autorotation"
        correction.data["sub_element"] = "correction"

        return self._add_rolls(Section.stack([pitch_break, autorotation, correction]), 0)

    def match_axis_rate(self, snap_rate: float, speed: float):
        return self.set_parameter()  # TODO should probably allow this somehow

    def match_intention(self, transform: Transformation, flown: Section):
        #TODO need to match flown pos/neg if F3A, not if IMAC
        return self.set_parameter(
            rolls=np.sign(np.mean(flown.gbrvel.x)) * abs(self.rolls)
        )

    @property
    def length(self):
        return self.create_template(Transformation(), 30.0, True).get_state_from_index(-1).pos.x