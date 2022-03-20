from geometry import Point, Quaternion, Transformation

import numpy as np
import pandas as pd
from typing import Union

from flightanalysis.base.table import Table, Constructs, SVar
from flightanalysis.state.variables import secvars



def make_bvel(sec) -> Point:
    wvel = sec.pos.diff(sec.dt)
    return sec.att.inverse().transform_point(wvel)

def make_brvel(sec) -> Point:
    return sec.att.body_diff(sec.dt).remove_outliers(3) 

def make_bacc(sec) -> Point:
    wacc = sec.att.transform_point(sec.vel).diff(sec.dt) + PZ(9.81, len(sec)) # assumes world Z is up
    return sec.att.inverse().transform_point(wacc)

def make_bracc(sec) -> Point:
    return sec.rvel.diff(sec.dt)



class State(Table):
    cols = Table.cols + Constructs(dict(
        pos  = SVar(Point,       ["x", "y", "z"]           , None       ), 
        att  = SVar(Quaternion,  ["rw", "rx", "ry", "rz"]  , None       ),
        vel  = SVar(Point,       ["u", "v", "w"]           , make_bvel  ),
        rvel = SVar(Point,       ["p", "q", "r"]           , make_brvel ),
        acc  = SVar(Point,       ["du", "dv", "dw"]        , make_bacc  ),
        racc = SVar(Point,       ["dp", "dq", "dr"]        , make_bracc ),
    ))


    @property
    def transform(self):
        return Transformation.build(self.pos, self.att)
    
    @property
    def back_transform(self):
        return Transformation(-self.pos, self.att.inverse())
     

    def from_transform(transform: Transformation, **kwargs): 
        if not "time" in kwargs.keys():
            kwargs["time"] = 0.0
        kwargs["pos"] = transform.translation
        kwargs["att"] = transform.rotation
        return State.from_constructs(**kwargs)

    def body_to_world(self, pin: Point) -> Point:
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
