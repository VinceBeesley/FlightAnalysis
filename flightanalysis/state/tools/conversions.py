
import numpy as np
import pandas as pd
from flightanalysis.state import State
from geometry import Quaternion, Coord, Point, P0, Transformation
from flightanalysis.model import Flow
from flightanalysis.environment import Environment


def convert_state(st: State, r: Point) -> State:
    att = st.att.body_rotate(r)
    q =  att.inverse() * st.att
    return State.from_constructs(
        time=st.time,
        pos=st.pos,
        att=att,
        vel=q.transform_point(st.vel),
        rvel=q.transform_point(st.rvel),
        acc=q.transform_point(st.acc),
        racc=q.transform_point(st.racc),
    )


def to_judging(st: State):
    """This rotates the body so the x axis is in the velocity vector"""
    return body_to_wind(st)

def body_to_stability(st: State, flow: Flow=None):
    if not flow:
        env = Environment.from_constructs(st.time)
        flow = Flow.build(st, env)
    return convert_state(st, -Point(0,1,0) * flow.alpha)    

def stability_to_wind(st: State, flow: Flow=None):
    if not flow:
        env = Environment.from_constructs(st.time)
        flow = Flow.build(st, env)
    return convert_state(st, Point(0,0,1) * flow.beta)

def body_to_wind(st: State, flow: Flow=None):
    return stability_to_wind(body_to_stability(st, flow), flow)


def judging_to_wind(st: State, flow: Flow):

    jwind = st.att.inverse().transform_point(flow.wind)

    angles = (jwind + st.vel).angles(st.vel)

    return State.from_constructs(
        st.time,
        pos=st.pos,
        att = st.att.body_rotate(angles)
    )

def wind_to_body(st: State, alpha, beta):
    return body_to_wind(st, -alpha, -beta)