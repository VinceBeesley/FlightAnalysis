from flightanalysis.state import State
import numpy as np
from geometry import Transformation, Quaternion, Coord, P0, PX, PY, PZ, Point


def direction(self):
    """returns 1 for going right, -1 for going left"""
    return np.sign(self.att.transform_point(Point(1, 0, 0)).x)
    

def inverted(self):
    return np.sign(self.att.transform_point(Point(0, 0, 1)).z) > 0

def upright(self):
    return not inverted(self)


def judging_itrans(self: State, template_itrans: Transformation):
    """The judging initial transform has its X axis in the states velocity vector and
    its wings aligned with the template"""
    return Transformation(
        self.pos[0], 
        Quaternion.from_rotation_matrix(
            Coord.from_xy(
                P0(), 
                self.att[0].transform_point(self.vel[0]),
                template_itrans.att.transform_point(PY()) 
            ).rotation_matrix()
        ).inverse()
    )