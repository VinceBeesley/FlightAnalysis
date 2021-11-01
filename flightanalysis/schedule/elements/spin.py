import numpy as np
from geometry import Transformation, Point, Points, Quaternion
from flightanalysis import Section, State
    
from . import El


class Spin(El):
    _speed_factor = 1 / 10

    def __init__(self, turns: float, opp_turns: float = 0.0, rate:float=1000, uid: str = None):
        super().__init__(uid)
        self.turns = turns
        self.opp_turns = opp_turns
        self.rate = rate

    def scale(self, factor):
        return self.set_parms(rate=self.rate / factor)

    def create_template(self, transform: Transformation, speed: float, simple: bool = False):
        _inverted = np.sign(transform.rotate(Point(0, 0, 1)).z)
        break_angle = np.radians(30) # pitch angle offset from vertical downline
        freq=1.0 if simple else Section._construct_freq 
        nose_drop_angle = np.pi/2 - abs(break_angle) #angle the nose has to drop through
        nose_drop_rate = self.rate / 5
        # The nose drop, assume it happens at the same rate as the spin
        nose_drop = Section.extrapolate_state(
            State.from_transform(transform), 
            nose_drop_angle / abs(nose_drop_rate), 
            freq
        ).superimpose_rotation(
            Point.Y(1.0), 
            nose_drop_angle * _inverted
        ) 
        nose_drop.data["sub_element"] = "nose_drop"

        # The axis (in body frame) about whitch the autorotation happens
        body_autorotation_axis = Quaternion.from_euler(
            (0, -_inverted * break_angle, 0)
        ).inverse().transform_point(Point(1,0,0))

        autoinit = State.from_transform(nose_drop[-1].transform, bvel=body_autorotation_axis * speed)

        autorotation = Section.extrapolate_state(
            autoinit, 2 * np.pi * abs(self.turns) / self.rate, freq=freq
        ).superimpose_rotation(body_autorotation_axis, 2 * np.pi * self.turns)
        autorotation.data["sub_element"] = "autorotation"

        if self.opp_turns == 0.0:
            pass
        else:
            opp_autorotation = Section.extrapolate_state(
                autorotation[-1], 2 * np.pi * abs(self.opp_turns) / self.rate , freq=freq
            ).superimpose_rotation(body_autorotation_axis, 2 * np.pi * self.opp_turns)
            opp_autorotation.data["sub_element"] = "opp_rotation"
            
            autorotation = Section.stack([autorotation, opp_autorotation])

        #correction to vertical downline
        correction = Section.extrapolate_state(
            autorotation[-1], 
            break_angle / abs(nose_drop_rate), freq=freq
        ).superimpose_rotation(Point(0, 1, 0), _inverted * break_angle )
        correction.data["sub_element"] = "correction"
        
        return self._add_rolls(Section.stack([nose_drop, autorotation, correction]), 0.0)


    def match_axis_rate(self, spin_rate, speed: float):
        return self.set_parms(rate=spin_rate)

    def match_intention(self, transform: Transformation, flown: Section):
        #TODO does not work for reversed spins
        gbmean = flown.gbrvel.mean()
        rate = np.sqrt(gbmean.x ** 2 + gbmean.z ** 2)
        return self.set_parms(
            turns=np.sign(gbmean.x) * abs(self.turns),
            opp_turns=0.0,
            rate = rate
        )
