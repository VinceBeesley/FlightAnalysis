from geometry import Point, Quaternion, Points, Quaternions, Transformation, cross_product
from geometry.point import cross_product
import numpy as np
import pandas as pd
from typing import Dict, Union
from json import load
from .svars import svars


class SVars(object):
    """Handles the variables described in svars.py"""

    def __init__(self, constructs=svars):
        self.constructs = constructs
        self.columns = np.array(list(dict.fromkeys(
            [col for construct in constructs.values() for col in construct]
        )))

    def __getattr__(self, name):
        if name in self.constructs:
            return self.constructs[name]
        else:
            raise AttributeError

    def __getitem__(self, indices):
        return self.columns[indices]


class State():
    """Describes the position and orientation of a body in 3D space.
    Uses a pandas series, with the SVars class to describe the index
    """
    vars = SVars()

    def __init__(
        self, 
        pos: Point, 
        att: Quaternion, 
        bvel: Point=Point.zeros(), 
        brvel: Point=Point.zeros(), 
        bacc: Point=Point.zeros(),
        **kwargs
    ):
        self.pos = pos
        self.att = att
        self.bvel = bvel
        self.brvel = brvel
        self.bacc = bacc
        self.misc = kwargs
        self.transform = Transformation(self.pos, self.att)
        self.back_transform = Transformation(-self.pos, self.att.inverse())

    def __getattr__(self, name):
        try:
            return self.misc[name]
        except KeyError:
            raise AttributeError(name)

    def copy(self, **args):
        new_inst = State(self.pos, self.att, self.bvel, self.brvel, self.bacc, **self.misc)
        for key, value in args.items():
            setattr(new_inst, key, value)
        return new_inst       

    @staticmethod
    def from_series(data: pd.Series):
        misc_keys = [key for key in data.keys() if not key in State.vars.columns]
        return State(
            Point(*data[State.vars.constructs['pos']]),
            Quaternion(*data[State.vars.constructs['att']]),
            Point(*data[State.vars.constructs['bvel']]),
            Point(*data[State.vars.constructs['brvel']]),
            Point(*data[State.vars.constructs['bacc']]),
            **{key: data[key] for key in misc_keys}
        )

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