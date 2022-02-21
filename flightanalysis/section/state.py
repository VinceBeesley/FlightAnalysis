from geometry import Point, Quaternion, Points, Quaternions, Transformation, cross_product
from geometry.point import cross_product
import numpy as np
import pandas as pd
from typing import Dict, Union, type
from json import load
from .variables import constructs

from flightanalysis.base.instant import Instant


class State(Instant):
    """Describes the the state of the aircraft
    """

    def __init__(self, data:dict):
        #assert_vars(data.keys())
        super().__init__(constructs, data)
        
        consts = self.existing_constructs()
        
        assert np.all([var in consts for var in ["pos", "att"]])

    @property
    def transform(self):
        return Transformation(self.pos, self.att)
    
    @property
    def back_transform(self):
        return Transformation(-self.pos, self.att.inverse())

    @staticmethod
    def from_constructs(**kwargs):
        cdicts = [constructs[key].todict(const) for key, const in list(kwargs.items())]
        return State({name:value for cdict in cdicts for name, value in cdict.items()})
      

    def from_transform(transform: Transformation, **kwargs): 
        if not "time" in kwargs.keys():
            kwargs["time"] = 0.0
        kwargs["pos"] = transform.translation
        kwargs["att"] = transform.rotation
        return State.from_constructs(**kwargs)

    def body_to_world(self, pin: Union[Point, Points]) -> Point:
        """Rotate a point in the body frame to a point in the data frame

        Args:
            pin (Point): Point on the aircraft

        Returns:
            Point: Point in the world
        """
        return self.transform.point(pin)

    @property
    def direction(self):
        if self.back_transform.rotate(Point(1, 0, 0)).x > 0:
            return "right"
        else:
            return "left"

