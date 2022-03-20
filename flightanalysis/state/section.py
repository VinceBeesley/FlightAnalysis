from geometry import Point
import numpy as np
import pandas as pd
from typing import Union
from numbers import Number

from flightanalysis.state.variables import secvars

class Section():
    _cols=secvars
        
    def body_to_world(self, pin: Point) -> pd.DataFrame:
        """generate world frame trace of a body frame point

        Args:
            pin (Point): point in the body frame
            pin (Points): points in the body frame

        Returns:
            Points: trace of points
        """

        if isinstance(pin, Point):
            return self.gatt.transform_point(pin) + self.gpos
        else:
            raise NotImplementedError

    def label(self, **kwargs):
        return Section(self.data.assign(**kwargs))

    def remove_labels(self):
        return Section(self.data.drop(["manoeuvre", "element"], 1, errors="ignore"))
    
    def flying_only(self):
        #TODO if gps drift this doesn't necessarily work
        above_ground = self.data.loc[self.data.z >= 5.0]
        return self[above_ground.index[0]:above_ground.index[-1]]

