import numpy as np
import pandas as pd
from geometry import Transformation, Point, PX, PY, PZ
from flightanalysis.state import State
    
from . import El


class StallTurn(El):
    def __init__(self, yaw_rate:float=3.0, uid: str = None):
        super().__init__(uid)
        self.yaw_rate = yaw_rate

    def scale(self, factor):
        return self.set_parms()

    def create_template(self, transform: Transformation, speed: float):
        return self._add_rolls(
            State.from_transform(transform, vel=Point.zeros()).extrapolate( 
                np.pi / abs(self.yaw_rate)
            ).superimpose_rotation(
                PZ(), 
                np.sign(self.yaw_rate) * np.pi
            ), 
            0.0
        )

    def match_axis_rate(self, yaw_rate: float, speed: float = 30.0):
        return self.set_parms(yaw_rate=yaw_rate)

    def match_intention(self, transform: Transformation, flown: State):
        return self.set_parms(
            yaw_rate=np.sign(flown.rvel.mean().z) * abs(self.yaw_rate), 
        )


