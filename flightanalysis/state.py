from geometry import Point, Quaternion
import numpy as np
import pandas as pd
from typing import Dict
from json import load


class SVars(object):
    """Handles the variables described in svars.json"""
    def __init__(self, constructs):
        self.constructs = constructs
        self.columns = np.array(list(dict.fromkeys(
            [col for construct in constructs.values() for col in construct]
        )))

    @staticmethod
    def from_json(file='flightanalysis/svars.json'):
        with open(file) as f:
            constructs = load(f)
        return SVars(constructs)

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
    vars = SVars.from_json()

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
    def from_posattvel(pos: Point, att: Quaternion, vel: Point):
        """Generate a State

        Args:
            pos (Point): [description]
            att (Quaternion): [description]
            vel (Point): [description]
        """
        dat = pd.Series()
        dat.index = State.columns

        dat[State.constructs['pos']] = list(pos)
        dat[State.constructs['att']] = list(att)
        dat[State.constructs['vel']] = list(vel)

        return State(dat.fillna(0))

    def body_to_world(self, pin: Point) -> Point:
        """Rotate a point in the body frame to a point in the data frame

        Args:
            pin (Point): Point on the aircraft

        Returns:
            Point: Point in the world
        """
        return Point(*self.pos) + Quaternion(*self.att).transform_point(pin)

    @staticmethod
    def construct_names(*args):
        return np.ndarray([State.constructs[name] for name in args]).flatten()
