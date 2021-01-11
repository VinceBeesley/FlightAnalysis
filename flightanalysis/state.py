from flightdata import Fields
from geometry import Point, Quaternion
from typing import Dict


class State():
    """Describes the position and orientation of a body in 3D space"""
    columns = 'x,y,z,dx,dy,dz,dx2,dy2,dz2,rw,rx,ry,rz,drw,drx,dry,drz,drw2,drx2,dry2,drz2'.split(
        ',')

    def __init__(self, data: Dict):
        self.data = data

    def __getattr__(self, name):
        if name in State.columns:
            return self.data[name]
        else:
            raise AttributeError

    def pos(self):
        return Point(self.x, self.y, self.z)

    def vel(self):
        return Point(self.dx, self.dy, self.dz)

    def att(self):
        return Quaternion(
            self.rw,
            Point(self.rx, self.ry, self.rz)
        )
