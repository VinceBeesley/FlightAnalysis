import numpy as np
from geometry import Transformation, Point, Points, Quaternion
from flightanalysis import Section, State

    
from . import El, Loop


class Spin(El):
    _speed_factor = 1 / 10

    def __init__(self, turns: float, opp_turns: float = 0.0, rate:float=700, uid: str = None):
        super().__init__(uid)
        self.turns = turns
        self.opp_turns = opp_turns
        self.rate = rate

    def scale(self, factor):
        return self.set_parms(rate=self.rate / factor)

    def create_template(self, transform: Transformation, speed: float, simple: bool = False):
        speed = speed * 0.5
        _inverted = np.sign(transform.rotate(Point(0, 0, 1)).z)
        break_angle = np.radians(30) # pitch angle offset from vertical downline
        freq=1.0 if simple else Section._construct_freq 
        
        nose_drop = Loop(15, -_inverted/4).create_template(transform, speed).superimpose_rotation(
            Point.Y(1.0), 
            -abs(break_angle) * _inverted
        ).label(sub_element="nose_drop")

        autorotation = Section.extrapolate_state(
            nose_drop[-1].copy(brvel=Point.zeros()), 
            (abs(self.turns + self.opp_turns) * 2*np.pi - 3*np.pi/2) / self.rate,
            freq=freq
        ).label(sub_element="autorotation")

        recovery = Section.extrapolate_state(
            autorotation[-1],
            np.pi / self.rate,
            freq=freq
        ).superimpose_rotation(
            Point.Y(1.0), 
            break_angle * _inverted
        ).label(sub_element="recovery")       
        
        no_spin = Section.stack([nose_drop, autorotation, recovery])
        
        if self.opp_turns == 0:
            spin=no_spin.smooth_rotation(Point(0,0,1), 2*np.pi*self.turns, "world", 0.3, 0.05)
        else:
            fwd_spin = no_spin.subset(
                0, 
                no_spin.duration * self.turns / (abs(self.turns) + abs(self.opp_turns))
            ).smooth_rotation(Point(0,0,1), 2*np.pi*self.turns, "world", 0.3, 0.05)

            aft_spin = no_spin.subset(
                no_spin.duration * self.opp_turns / (abs(self.turns) + abs(self.opp_turns)),
                -1
            )
            aft_spin=aft_spin.superimpose_angles(
                Points.from_point(
                    Point(0,0,1) * 2 * np.pi * self.turns, 
                    len(aft_spin.data)
                ), 
                "world"
            ).smooth_rotation(Point(0,0,1), -2*np.pi*self.opp_turns, "world", 0.05, 0.05)

            spin = Section.stack([fwd_spin, aft_spin])

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
