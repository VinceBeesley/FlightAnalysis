import numpy as np
from geometry import Transformation, Point, Quaternion, PX, PY, PZ
from flightanalysis.state import State
from flightanalysis.base.table import Time
from . import El, Loop, DownGrades, DownGrade
from flightanalysis.criteria import *


class Spin(El):
    _speed_factor = 1 / 10
    parameters = El.parameters + "turns,opp_turns,rate,break_angle".split(",")
    def __init__(self, speed: float, turns: float, opp_turns: float = 0.0, rate:float=700, break_angle=30, uid: str=None):
        super().__init__(uid, speed)
        self.turns = turns
        self.opp_turns = opp_turns
        self.rate = rate
        self.break_angle = break_angle

    @property
    def intra_scoring(self):
        return DownGrades([
            DownGrade("roll_amount", "measure_end_roll_angle", basic_angle_f3a)
        ])


    def to_dict(self):
        return dict(
            kind=self.__class__.__name__,
            turns=self.turns,
            opp_turns=self.opp_turns,
            rate=self.rate,
            speed=self.speed,
            uid=self.uid
        )

    def describe(self):
        opp = "" if self.opp_turns == 0 else f", {self.opp_turns} opposite, "
        return f"{self.turns} turn spin,{opp} rate={self.rate}"


    def scale(self, factor):
        return self.set_parms(rate=self.rate / factor)

    def create_nose_drop(self, transform: Transformation, time:Time=None):
        _inverted = transform.rotation.is_inverted()[0]

        return Loop(self.speed*0.5, 7.5, np.pi*_inverted/2).create_template(
            transform, time
        ).superimpose_rotation(
            PY(), 
            -abs(self.break_angle) * _inverted
        ).label(sub_element="nose_drop")

    def create_autorotation(self, transform: Transformation, time: Time=None):
        pass

    def create_template(self, transform: Transformation, time: Time=None):
        speed = self.speed * 0.5
        _inverted = transform.rotation.is_inverted()[0]
        break_angle = np.radians(30) # pitch angle offset from vertical downline
        
        nose_drop = Loop(speed, 7.5, np.pi*_inverted/2).create_template(transform).superimpose_rotation(
            PY(), 
            -abs(break_angle) * _inverted
        ).label(sub_element="nose_drop")

        autorotation = State.extrapolate(
            nose_drop[-1].copy(rvel=Point.zeros()), 
            ((abs(self.turns) + abs(self.opp_turns)) * 2*np.pi - 3*np.pi/2) / abs(self.rate)
        ).label(sub_element="autorotation")

        recovery = State.extrapolate(
            autorotation[-1],
            abs(np.pi / self.rate),
        ).superimpose_rotation(
            PY(), 
            break_angle * _inverted
        ).label(sub_element="recovery")       
        
        no_spin = State.stack([nose_drop, autorotation, recovery])
        
        if self.opp_turns == 0:
            spin=no_spin.smooth_rotation(Point(0,0,1), 2*np.pi*self.turns, "world", 0.3, 0.05)
        else:
            fwd_spin = no_spin[
                0:no_spin.duration * self.turns / (abs(self.turns) + abs(self.opp_turns))
            ].smooth_rotation(Point(0,0,1), 2*np.pi*self.turns, "world", 0.3, 0.05)

            aft_spin = no_spin[
                no_spin.duration * self.opp_turns / (abs(self.turns) + abs(self.opp_turns)):
                
            ]
            aft_spin=aft_spin.superimpose_angles(
                (PZ() * 2 * np.pi * self.turns).tile( 
                    len(aft_spin.data)
                ), 
                "world"
            ).smooth_rotation(PZ(), -2*np.pi*self.opp_turns, "world", 0.05, 0.05)

            spin = State.stack([fwd_spin, aft_spin])

        return self._add_rolls(spin, 0.0)


    def match_axis_rate(self, spin_rate, speed: float):
        return self.set_parms(rate=spin_rate)

    def match_intention(self, transform: Transformation, flown: State):
        #TODO does not work for reversed spins
        gbmean = flown.rvel.mean()
        rate = np.sqrt(gbmean.x[0] ** 2 + gbmean.z[0] ** 2)
        return self.set_parms(
            turns=np.sign(gbmean.x[0]) * abs(self.turns),
            opp_turns=0.0,
            rate = rate
        )

    def copy_direction(self, other):
        return self.set_parms(
            turns=abs(self.turns) * np.sign(other.turns),
            opp_turns=abs(self.opp_turns) * np.sign(other.opp_turns),
        )