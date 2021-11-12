from geometry import Point, Quaternion, Points, Quaternions, Transformation, cross_product
from geometry.point import cross_product
import numpy as np
import pandas as pd
from typing import Dict, Union
from json import load
from .svars import subset_vars, constructs, assert_vars, assert_constructs, all_vars


class State():
    """Describes the the state of the aircraft
    """

    def __init__(self, data:dict):
        assert_vars(data.keys())
        self.data = data

    def __getattr__(self, name):
        if name in self.data.keys():
            return self.data[name]
        elif name in constructs.keys():
            return constructs[name].fromdict(self.data)
 
    @property
    def transform(self):
        return Transformation(self.pos, self.att)
    
    @property
    def back_transform(self):
        return Transformation(-self.pos, self.att.inverse())

    @staticmethod
    def from_constructs(**kwargs):
        assert_constructs(kwargs.keys())

        cdicts = [constructs[key].todict(const) for key, const in kwargs.items()]

        return State({name:value for cdict in cdicts for name, value in cdict.items()})

    def existing_constructs(self):
        return [key for key, const in constructs.items() if all([val in self.data.keys() for val in const.keys])]

    def copy(self, *args,**kwargs):
        kwargs = dict(kwargs, **{list(constructs.keys())[i]: arg for i, arg in enumerate(args)})
        
        old_constructs = {key: self.__getattr__(key) for key in self.existing_constructs() if not key in kwargs}

        new_constructs = {key: value for key, value in list(kwargs.items()) + list(old_constructs.items())}

        return State.from_constructs(**new_constructs)
        

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