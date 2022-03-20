
import numpy as np
import pandas as pd
from flightanalysis.state import Section
from geometry import Quaternion, Quaternions, Coord, Point, Points



def to_judging(self: Section):
    """This rotates the body so the x axis is in the velocity vector"""
    
    angles = Points.angles(
        Points.X(np.ones(len(self.data))), 
        self.gbvel.unit()
    )  # == theta * nhat

    return Section.from_constructs(
        self.gtime,
        pos=self.gpos,
        att = self.gatt.body_rotate(angles)
    )


def body_to_wind(self: Section, alpha, beta):
    return Section.from_constructs(
        self.gtime,
        pos=self.gpos,
        att=self.gatt.body_rotate(Points(np.array([np.zeros(len(alpha)), -alpha, beta]).T))
    )

def judging_to_wind(self: Section, wind: Points):
    jwind = self.gatt.inverse().transform_point(wind)
    angles = Points.angles(jwind + self.gbvel, self.gbvel)

    return Section.from_constructs(
        self.gtime,
        pos=self.gpos,
        att = self.gatt.body_rotate(angles)
    )

def wind_to_body(self: Section, alpha, beta):
    return body_to_wind(self, -alpha, -beta)