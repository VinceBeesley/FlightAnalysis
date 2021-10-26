import numpy as np
import pandas as pd
from geometry import Transformation, Points, scalar_projection
from flightanalysis import Section
    
from . import El


class StallTurn(El):
    _speed_scale = 1 / 20

    def __init__(self, direction: int = 1, width: float = 1.0, uid: str = None):
        super().__init__(uid)
        self.direction = direction
        self.width = width

    def set_parameter(self, direction=None, width=None):
        return StallTurn(
            direction if direction is not None else self.direction,
            width if width is not None else self.width,
            self.uid
        )

    def scale(self, factor):
        return self.set_parameter()

    def create_template(self, transform: Transformation, speed: float, simple: bool = False):
        el = Section.from_loop(
            transform,
            StallTurn._speed_scale * speed,
            0.5 * self.direction,
            self.width / 2,
            True,
            freq=1.0 if simple else None)
        return self._add_rolls(el, 0.0)

    def match_axis_rate(self, yaw_rate: float, speed: float):
        return self.set_parameter(width=2 * StallTurn._speed_scale * speed / yaw_rate)

    def match_intention(self, transform: Transformation, flown: Section):
        return self.set_parameter(
            direction=np.sign(np.mean(Points.from_pandas(flown.brvel).z)),
            width=0.5
        )


