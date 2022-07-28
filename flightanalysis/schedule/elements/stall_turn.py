import numpy as np
import pandas as pd
from geometry import Transformation, Point, PX, PY, PZ
from flightanalysis.state import State
    
from . import El


class StallTurn(El):
    parameters = El.parameters + ["yaw_rate"]
    def __init__(self, speed:float, yaw_rate:float=3.0, uid: str=None):
        super().__init__(uid, speed)
        self.yaw_rate = yaw_rate

    def scale(self, factor):
        return self.set_parms()

    def create_template(self, transform: Transformation):
        return self._add_rolls(
            State.from_transform(transform, vel=Point.zeros()).extrapolate( 
                np.pi / abs(self.yaw_rate)
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
            yaw_rate=np.sign(flown.r.mean().z[0]) * abs(self.yaw_rate), 
        )


