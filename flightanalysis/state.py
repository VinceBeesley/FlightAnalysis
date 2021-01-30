from geometry import Point, Quaternion, Points, Quaternions, Transformation
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

    def __init__(self, data: pd.Series):
        self.data = data

    def __getattr__(self, name):
        if name in State.vars:
            return self.data[name]
        elif name in State.vars.constructs:
            return tuple(self.data[State.vars.constructs[name]])
        else:
            raise AttributeError

    @staticmethod
    def from_posattvel(pos: Point, att: Quaternion, bvel: Point):
        """Generate a State

        Args:
            pos (Point): [description]
            att (Quaternion): [description]
            vel (Point): [description]
        """
        dat = pd.Series(index=State.vars.columns)
        dat[State.vars.constructs['pos']] = list(pos)
        dat[State.vars.constructs['att']] = list(att)
        dat[State.vars.constructs['bvel']] = list(bvel)
        dat[State.vars.constructs['brvel']] = np.zeros(3)
        return State(dat.fillna(0))

    def body_to_world(self, pin: Union[Point, Points]) -> Point:
        """Rotate a point in the body frame to a point in the data frame

        Args:
            pin (Point): Point on the aircraft

        Returns:
            Point: Point in the world
        """
        if isinstance(pin, Point):
            return Point(*self.pos) + Quaternion(*self.att).transform_point(pin)
        elif isinstance(pin, Points):
            return Points.from_point(*self.pos, pin.count) + \
                Quaternions.from_quaternion(
                    *self.att, pin.count).transform_point(pin)
        else:
            return NotImplemented

    @staticmethod
    def construct_names(*args):
        return np.ndarray([State.constructs[name] for name in args]).flatten()

    @property
    def transform(self):
        return Transformation(Point(*self.pos), Quaternion(*self.att))

    @property
    def transform_to(self):
        return Transformation(-Point(*self.pos), Quaternion(*self.att).inverse())
