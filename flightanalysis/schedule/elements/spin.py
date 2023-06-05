import numpy as np
from geometry import Transformation, Point, Quaternion, PX, PY, PZ
from flightanalysis.state import State
from flightanalysis.base.table import Time
from . import El, Loop, DownGrades, DownGrade, Elements
from flightanalysis.criteria import *



class Spin(El):
    parameters = El.parameters + "turns,opp_turns,rate,break_angle".split(",")
    def __init__(self, speed: float, turns: float, opp_turns: float = 0.0, rate:float=1.8, break_angle=np.radians(20), uid: str=None):
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


    def _create_nose_drop(self, transform: Transformation, flown:State=None):
        _inverted = transform.rotation.is_inverted()[0]

        return Loop(self.speed, 7.5, np.pi*_inverted/2).create_template(
            transform, flown
        ).superimpose_rotation(
            PY(), 
            -abs(self.break_angle) * _inverted
        ).label(sub_element="nose_drop")

    def _create_autorotation(self, transform: Transformation, flown: State=None):
        return State.from_transform(
            transform, 
            vel=transform.att.inverse().transform_point(PZ(-self.speed)) 
        ).fill(
            El.create_time(
                ((abs(self.turns) + abs(self.opp_turns)) * 2*np.pi - 3*np.pi/2) / abs(self.rate), 
                flown
            )
        ).label(sub_element="autorotation")

    def _create_recovery(self, transform: Transformation, flown: State=None):
        return State.from_transform(
            transform, 
            vel = transform.att.inverse().transform_point(PZ(-self.speed)) 
        ).fill(
            El.create_time(abs(np.pi / self.rate), flown)
        ).superimpose_rotation(
            PY(), 
            self.break_angle * transform.rotation.is_inverted()[0]
        ).label(sub_element="recovery")       
    

    def create_template(self, transform: Transformation, flown: State=None):
        snd=None
        sau=None
        sre=None
        
        if flown is not None:
            snd = flown.get_subelement("nose_drop")
            sau = flown.get_subelement("autorotation")
            sre = flown.get_subelement("recovery")

        nose_drop = self._create_nose_drop(transform, snd)
        autorotation = self._create_autorotation(nose_drop[-1].transform, sau)
        correction = self._create_recovery(autorotation[-1].transform, sre)

        no_spin = State.stack([nose_drop,autorotation, correction])
        
        if self.opp_turns == 0:
            spin=no_spin.smooth_rotation(Point(0,0,1), 2*np.pi*self.turns, "world", 0.3, 0.05)
        else:
            fwd_spin = no_spin[
                :no_spin.duration * self.turns / (abs(self.turns) + abs(self.opp_turns))
            ].smooth_rotation(Point(0,0,1), 2*np.pi*self.turns, "world", 0.3, 0.05)
            
            fwd_spin.data.loc[fwd_spin.sub_element=="autorotation","sub_element"] == "autorotation_1"

            aft_spin = no_spin[
                no_spin.duration * self.opp_turns / (abs(self.turns) + abs(self.opp_turns)):
            ]
            aft_spin=aft_spin.superimpose_angles(
                (PZ() * 2 * np.pi * self.turns).tile(len(aft_spin.data)), 
                "world"
            ).smooth_rotation(PZ(), -2*np.pi*self.opp_turns, "world", 0.05, 0.05)

            aft_spin.data.loc[aft_spin.data.sub_element=="autorotation","sub_element"] == "autorotation_2"

            spin = State.stack([fwd_spin, aft_spin])

        return self._add_rolls(spin, 0.0)
        

    def match_axis_rate(self, spin_rate, speed: float):
        return self.set_parms(rate=spin_rate)

    def match_intention(self, transform: Transformation, flown: State):
        #TODO does not work for reversed spins
        wrvel = flown.att.transform_point(flown.rvel)

        # Also the direction is not working
        return self.set_parms(
            speed = flown.vel.x.mean(),
            turns=np.sign(wrvel.z.mean()) * abs(self.turns),
            opp_turns=0.0,
            rate = np.abs(wrvel.z).max()
        )

    def copy_direction(self, other):
        return self.set_parms(
            turns=abs(self.turns) * np.sign(other.turns),
            opp_turns=abs(self.opp_turns) * np.sign(other.opp_turns),
        )