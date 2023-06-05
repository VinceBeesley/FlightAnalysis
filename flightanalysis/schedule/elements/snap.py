import numpy as np
from geometry import Transformation, Quaternion, Point, Euler, PX, PY, PZ, P0, Coord
from flightanalysis.state import State
from flightanalysis.base.table import Time
from . import El, Line, DownGrades, DownGrade
from flightanalysis.criteria import *
from typing import Union

class Snap(El):
    parameters = El.parameters + "rolls,direction,rate,length,break_angle,pitch_rate".split(",")
    break_angle = np.radians(10)
    def __init__(self, speed:float, rolls: float, rate:float, direction:int=1, break_angle: float=np.radians(10), pitch_rate:float=10, uid: str=None):
        super().__init__(uid, speed)
        self.rolls = rolls
        self.direction = direction
        self.rate = rate
        self.break_angle = break_angle
        self.pitch_rate = pitch_rate
        self._rotation_axis = Euler(
            0, 
            self.direction * self.break_angle, 
            0
        ).inverse().transform_point(PX())

    @property
    def intra_scoring(self):
        return DownGrades([
            DownGrade("roll_amount", "measure_end_roll_angle", basic_angle_f3a)
        ])

    def to_dict(self):
        return dict(
            kind=self.__class__.__name__,
            rolls=self.rolls,
            rate=self.rate,
            direction=self.direction,
            speed=self.speed,
            uid=self.uid
        )

    def describe(self):
        d1 = "positive" if self.direction==1 else "negative"
        return f"{self.rolls} {d1} snap, rate={self.rate}"

    @staticmethod
    def length(speed, rolls, rate):
        return speed * 2 * np.pi * (2 * Snap.break_angle + abs(rolls)) / rate

    def scale(self, factor):
        return self.set_parms(rate=self.rate/factor)        

    def _create_break(self, istate: State, flown: State=None) -> State:
        return istate.fill( 
            El.create_time(2 * np.pi * self.break_angle / self.pitch_rate, flown)
        ).superimpose_rotation(
            PY(), 
            self.direction * self.break_angle
        )

    def _create_autorotation(self, istate: State, flown: State=None) -> State:
        
        return istate.fill(
            El.create_time(2 * np.pi * abs(self.rolls) / self.rate, flown).reset_zero()
        ).superimpose_rotation(
            self._rotation_axis, 
            2 * np.pi * self.rolls,
        )

    def _create_correction(self, istate: State, flown: State=None) -> State:
        return istate.fill(
            El.create_time(2 * np.pi * self.break_angle / self.pitch_rate, flown).reset_zero()
        ).superimpose_rotation(
            PY(), 
            -self.direction * self.break_angle
        )

    def create_template(self, istate: Union[State, Transformation], flown:State=None) -> State:
        sbr=None
        sau=None
        sco=None
        
        if flown is not None:
            sbr = flown.get_subelement("pitch_break")
            sau = flown.get_subelement("autorotation")
            sco = flown.get_subelement("correction")
        
        istate = El._create_istate(istate, self.speed)

        pitch_break = self._create_break(istate[-1], sbr).label(sub_element="pitch_break")
        autorotation = self._create_autorotation(pitch_break[-1], sau).label(sub_element="autorotation")
        correction = self._create_correction(autorotation[-1], sco).label(sub_element="correction")

        return self._add_rolls(State.stack([pitch_break, autorotation, correction]), 0.0)


    def match_axis_rate(self, snap_rate: float):
        return self.set_parms()  # TODO should probably allow this somehow

    def match_intention(self, transform: Transformation, flown: State):
        #TODO need to match flown pos/neg if F3A, not if IMAC
        return self.set_parms(
            rolls=np.sign(flown.rvel.mean().x)[0] * abs(self.rolls)
        )

    @property
    def length(self):
        return self.create_template(Transformation())[-1].pos.x[-1]

    def copy_direction(self, other):
        return self.set_parms(
            rolls=abs(self.rolls) * np.sign(other.rolls),
            direction = other.direction
        )


   