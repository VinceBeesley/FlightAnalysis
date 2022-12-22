import numpy as np
import pandas as pd
from geometry import Transformation, Point, PX, PY, PZ
from flightanalysis.state import State
    
from . import El, DownGrades, DownGrade
from flightanalysis.criteria import *


class StallTurn(El):
    parameters = El.parameters + ["yaw_rate"]
    def __init__(self, speed:float, yaw_rate:float=3.0, uid: str=None):
        super().__init__(uid, speed)
        self.yaw_rate = yaw_rate

    @property
    def intra_scoring(self):
        return DownGrades([
            DownGrade("roll_angle", "measure_roll_angle_error", intra_f3a_angle)
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

    def create_template(self, transform: Transformation, flown: State=None):
        return self._add_rolls(
            State.from_transform(transform, vel=Point.zeros()).fill( 
                El.create_time(np.pi / abs(self.yaw_rate), flown)
            ).superimpose_rotation(
                PZ(), 
                np.sign(self.yaw_rate) * np.pi
            ), 
            0.0
        )

    def match_axis_rate(self, yaw_rate: float):
        return self.set_parms(yaw_rate=yaw_rate)

    def match_intention(self, transform: Transformation, flown: State):
        return self.set_parms(
            yaw_rate=flown.data.r[flown.data.r.abs().idxmax()]
        )

    def copy_direction(self, other):
        return self.set_parms(
            yaw_rate=abs(self.yaw_rate) * np.sign(other.yaw_rate)
        )