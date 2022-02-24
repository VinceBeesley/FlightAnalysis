from geometry import Point, Points, Transformation

import numpy as np
import pandas as pd
from typing import Union

from flightanalysis.base import Instant
from flightanalysis.section.variables import secvars



class State(Instant):
    _cols=secvars



    @property
    def transform(self):
        return Transformation(self.pos, self.att)
    
    @property
    def back_transform(self):
        return Transformation(-self.pos, self.att.inverse())

    @staticmethod
    def from_constructs(**kwargs):
        cdicts = [secvars.data[key].todict(const) for key, const in list(kwargs.items())]
        return State({name:value for cdict in cdicts for name, value in cdict.items()})
      

    def from_transform(transform: Transformation, **kwargs): 
        if not "time" in kwargs.keys():
            kwargs["time"] = 0.0
        kwargs["pos"] = transform.translation
        kwargs["att"] = transform.rotation
        return State.from_constructs(**kwargs)

    def body_to_world(self, pin: Union[Point, Points]) -> Point:
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

    def copy(self, *args,**kwargs):
        kwargs = dict(kwargs, **{list(self.cols.data.keys())[i]: arg for i, arg in enumerate(args)}) # add the args to the kwargs

        old_constructs = {key: self.__getattr__(key) for key in self.cols.existing(self.data.index).data if not key in kwargs}
        
        new_constructs = {key: value for key, value in list(kwargs.items()) + list(old_constructs.items())}

        return State.from_constructs(**new_constructs)