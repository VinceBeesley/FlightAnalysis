from geometry import Point, Quaternion
import numpy as np
import pandas as pd


class State():
    """Describes the position and orientation of a body in 3D space
        Position and attitude in world frame, velocities and accelerations in body frame.
    """

    constructs = {
        'pos': ['x', 'y', 'z'],
        'att': ['rw', 'rx', 'ry', 'rz'],
        'vel': ['vx', 'vy', 'vz'],
        'rvel': ['rvw', 'rvx', 'rvy', 'rvz'],
        'acc': ['ax', 'ay', 'az'],
        'racc': ['raw', 'rax', 'ray', 'raz']
    }

    columns = np.ndarray(constructs.values()).flatten()

    def __init__(self, data):
        self.data = data

    def __getattr__(self, name):
        if name in State.columns:
            return self.data[name]
        elif name in State.constructs:
            return tuple(self.data[State.constructs[name]])
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