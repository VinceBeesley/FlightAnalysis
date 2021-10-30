import numpy as np
import pandas as pd
from geometry import Transformation, Points, Point
from flightanalysis import Section, State
    
from . import El


class StallTurn(El):
    def __init__(self, yaw_rate:float=3.0, uid: str = None):
        super().__init__(uid)
        self.yaw_rate = yaw_rate
        
    def set_parameter(self, yaw_rate=None):
        return StallTurn(
            yaw_rate if yaw_rate is not None else self.yaw_rate,
            self.uid
        )

    def scale(self, factor):
        return self.set_parameter()

    def create_template(self, transform: Transformation, speed: float, simple: bool = False):
        return self._add_rolls(
            Section.extrapolate_state(
                State(transform.translation, transform.rotation), 
                2*np.pi / abs(self.yaw_rate), 
                1.0 if simple else Section._construct_freq
            ).superimpose_rotation(
                Point.Z(1.0), 
                np.sign(self.yaw_rate) / 2
            ), 
            0.0
        )

    def match_axis_rate(self, yaw_rate: float, speed: float = 30.0):
        return self.set_parameter(yaw_rate)

    def match_intention(self, transform: Transformation, flown: Section):
        return self.set_parameter(
            direction=np.sign(np.mean(flown.gbrvel.z)),
            width=0.5
        )


