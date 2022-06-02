from flightanalysis.state import State
import numpy as np
from geometry import Point





def direction(self):
    """returns 1 for going right, -1 for going left"""
    return np.sign(self.att.transform_point(Point(1, 0, 0)).x)
    