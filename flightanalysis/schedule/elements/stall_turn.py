from __future__ import annotations
import numpy as np
from geometry import Transformation, PX, PY, PZ, P0
from flightanalysis.state import State
from flightanalysis.base import Time
from .element import Element
from flightanalysis.schedule.scoring import *


class StallTurn(Element):
    parameters = Element.parameters + ["yaw_rate"]
    def __init__(self, speed:float, yaw_rate:float=3.0, uid: str=None):
        super().__init__(uid, speed)
        self.yaw_rate = yaw_rate

    @property
    def intra_scoring(self) -> DownGrades:
        return DownGrades([
            DownGrade(Measurement.roll_angle, f3a.intra_roll)
        ])

    def to_dict(self):
        return dict(
            kind=self.__class__.__name__,
            yaw_rate=self.yaw_rate,
            speed=self.speed,
            uid=self.uid
        )

    def describe(self):
        return f"stallturn, yaw rate = {self.yaw_rate}"

    def create_template(self, istate: State, time: Time=None) -> State:
        return self._add_rolls(
            istate.copy(rvel=P0() ,vel=P0()).fill( 
                Element.create_time(np.pi / abs(self.yaw_rate), time)
            ).superimpose_rotation(
                PZ(), 
                np.sign(self.yaw_rate) * np.pi
            ), 
            0.0
        )

    def match_axis_rate(self, yaw_rate: float) -> StallTurn:
        return self.set_parms(yaw_rate=yaw_rate)

    def match_intention(self, transform: Transformation, flown: State) -> StallTurn:
        return self.set_parms(
            yaw_rate=flown.data.r[flown.data.r.abs().idxmax()]
        )

    def copy_direction(self, other) -> StallTurn:
        return self.set_parms(
            yaw_rate=abs(self.yaw_rate) * np.sign(other.yaw_rate)
        )