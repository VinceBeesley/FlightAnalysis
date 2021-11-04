import numpy as np
from geometry import Transformation, Point, Points, Quaternion
from flightanalysis import Section, State

    
from . import El, Loop


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
        speed = speed *2/3
        _inverted = np.sign(transform.rotate(Point(0, 0, 1)).z)
        break_angle = np.radians(30) # pitch angle offset from vertical downline
        freq=1.0 if simple else Section._construct_freq 
        
        # The nose drop, happens in the first half turn

        nose_drop = Loop(15, -0.25 * _inverted).create_template(transform, speed).superimpose_rotation(
            Point.Y(1.0), 
            -abs(break_angle) * _inverted
        )

#        nose_drop = Section.extrapolate_state(
#            State.from_transform(transform, bvel=Point(0,0,- _inverted * speed)), 
#            0.5*np.pi / self.rate,
#            freq
#        ).superimpose_rotation(
#            Point.Y(1.0), 
#            (np.pi/2 - abs(break_angle)) * _inverted
#        ) 

        nose_drop.data["sub_element"] = "nose_drop"

        if self.opp_turns == 0.0:
            autorotation = Section.extrapolate_state(
                nose_drop[-1].copy(brvel=Point.zeros()), 
                (abs(self.turns) * 2*np.pi - 3*np.pi/4) / self.rate,
                freq=freq
            )
            autorotation.data["sub_element"] = "autorotation"

            recovery = Section.extrapolate_state(
                autorotation[-1],
                np.pi / (4*self.rate),
                freq=freq
            ).superimpose_rotation(
                Point.Y(1.0), 
                break_angle * _inverted
            ) 
            recovery.data["sub_element"] = "recovery"
            spin = Section.stack([nose_drop, autorotation, recovery]).superimpose_rotation(Point(0,0,1), 2*np.pi*self.turns, "world")
        else:
            autorotation = Section.extrapolate_state(
                nose_drop[-1].copy(brvel=Point.zeros()), 
                (abs(self.turns) * 2*np.pi - np.pi/2) / self.rate,
                freq=freq
            )
            autorotation.data["sub_element"] = "autorotation"

            first_part = Section.stack([nose_drop, autorotation]).superimpose_rotation(Point(0,0,1), 2*np.pi*self.turns, "world")


            opprotation = Section.extrapolate_state(
                first_part[-1].copy(brvel=Point.zeros()), 
                (abs(self.opp_turns) * 2 * np.pi - np.pi/4) / self.rate,
                freq=freq
            )
            opprotation.data["sub_element"] = "autorotation"

            recovery = Section.extrapolate_state(
                autorotation[-1],
                np.pi / (4*self.rate),
                freq=freq
            ).superimpose_rotation(
                Point.Y(1.0), 
                break_angle * _inverted
            ) 
            recovery.data["sub_element"] = "recovery"

            second_part = Section.stack([opprotation, recovery]).superimpose_rotation(Point(0,0,1), -2*np.pi*self.opp_turns, "world")

            spin = Section.stack([first_part, second_part])


        return self._add_rolls(spin, 0.0)


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
