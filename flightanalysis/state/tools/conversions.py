
import numpy as np
import pandas as pd
from flightanalysis.state import State
from geometry import Quaternion, Coord, Point



def to_judging(st: State):
    """This rotates the body so the x axis is in the velocity vector"""
    
    angles = Point.angles(
        Point.X(np.ones(len(st.data))), 
        st.vel.unit()
    )  # == theta * nhat

    return State.from_constructs(
        st.time,
        pos=st.pos,
        att = st.att.body_rotate(angles)
    )


def body_to_wind(st: State, alpha, beta):
    return State.from_constructs(
        st.time,
        pos=st.pos,
        att=st.att.body_rotate(Point(np.array([np.zeros(len(alpha)), -alpha, beta]).T))
    )

def judging_to_wind(st: State, wind: Point):
    jwind = st.att.inverse().transform_point(wind)
    angles = Point.angles(jwind + st.vel, st.vel)

    return State.from_constructs(
        st.time,
        pos=st.pos,
        att = st.att.body_rotate(angles)
    )

def wind_to_body(st: State, alpha, beta):
    return body_to_wind(st, -alpha, -beta)