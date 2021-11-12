"""These are the variables handled by the State and Section classes.
    The variables are defined in the values of the svars dict, in the order in which they first appear.
    The keys just provide some handy tags to access sets of values with. 

    pos = position (Cartesian)
    att = attitude (Quaternion)
    bvel = velocity in (body frame)
    brvel = rotational velocity (body axis rates)

    """
from geometry import Point, Points, Quaternion, Quaternions, Transformation
import numpy as np
import pandas as pd

class SVar:
    def __init__(self, names, single, multiple, description):
        self.names = names
        self.single = single
        self.multiple = multiple
        self.description = description
    
    @property
    def prefix(self):
        return self.names[0][:len(self.names[0])-1]

svars = {
    "time": SVar(["tl", "tg"], dict, pd.DataFrame, ""),
    "pos": SVar(["x", "y", "z"], Point, Points, ""),
    "att": SVar(["rw", "rx", "ry", "rz"], Quaternion, Quaternions, ""),
    "bvel": SVar(["bvx", "bvy", "bvz"], Point, Points, ""),
    "brvel": SVar(["brvr", "brvp", "brvy"], Point, Points, ""),
    "bacc": SVar(["bax", "bay", "baz"], Point, Points, ""),
    "wind": SVar(["wvx", "wvy", "wvz"], Point, Points, ""),
    "bwind": SVar(["bwvx", "bwvy", "bwvz"], Point, Points, ""),
    "aoa": SVar(["aoaa", "aoab"], dict, pd.DataFrame, ""),
}

