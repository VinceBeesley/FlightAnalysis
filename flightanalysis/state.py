from geometry import Point, Quaternion
import numpy as np
import pandas as pd


class State():
    """Describes the position and orientation of a body in 3D space"""
    columns = 'x,y,z,dx,dy,dz,dx2,dy2,dz2,rw,rx,ry,rz,drw,drx,dry,drz,drw2,drx2,dry2,drz2'.split(
        ',')
    constructs = {
        'pos': ['x', 'y', 'z'],
        'att': ['rw', 'rx', 'ry', 'rz'],
        'vel': ['dx', 'dy', 'dz'],
        'rvel': ['drw', 'drx', 'dry', 'drz'],
        'acc': ['dx2', 'dy2', 'dz2'],
        'racc': ['drw2', 'drx2', 'dry2', 'drz2']
    }

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

        dat = np.zeros(shape=(1, len(State.columns)))
        dat[:, 0:3] = pos.to_list()  # initial position
        dat[:, 3:6] = vel.to_list()  # initial velocity
        dat[:, 9:13] = att.to_list()  # initial attitude

        return State(pd.DataFrame(dat, columns=State.columns).iloc[0])
