from geometry import Point, Quaternion, Points, Quaternions, Transformation, cross_product
from geometry.point import cross_product
import numpy as np
import pandas as pd
from typing import Dict, Union
from json import load
from .svars import svars


class State():
    """Describes the the state of the aircraft
    """

    def __init__(self, data:dict):
        self.data = data

    def __getattr__(self, name):
        if name in self.data.keys():
            return self.data[name]
        elif name in svars.keys():
            return svars[name].single(*[self.data[name] for name in svars[name].names])
 
    @property
    def transform(self):
        return Transformation(self.pos, self.att)
    
    @property
    def back_transform(self):
        return Transformation(-self.pos, self.att.inverse())

    @staticmethod
    def from_constructs(**kwargs):
        return State({name:value for key, const in kwargs.items() for name, value in const.to_dict(svars[key].prefix)})

    def from_transform(transform: Transformation, **kwargs): 
        return State(transform.translation, transform.rotation, **kwargs)

    def body_to_world(self, pin: Union[Point, Points]) -> Point:
        """Rotate a point in the body frame to a point in the data frame

        Args:
            pin (Point): Point on the aircraft

        Returns:
            Point: Point in the world
        """
        return self.transform.point(pin)

    @property
    def vel(self):
        return self.transform.rotate(self.bvel)

    @property
    def direction(self):
        if self.back_transform.rotate(Point(1, 0, 0)).x > 0:
            return "right"
        else:
            return "left"