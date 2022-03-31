
import numpy as np
import pandas as pd
from flightanalysis.state import State
from geometry import Quaternion, Coord, Point, P0, Transformation, PX
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


def judging_to_wind(st: State, env: Environment) -> State:
    """I think the correct way to go from judging axis to wind axis is to do a yaw rotation then a pitch 
    rotation, as this keeps the wing vector in the judging axis XY plane.

    Args:
        st (State): the judging axis data
        env (Environment): the environment

    Returns:
        State: the wind axis data
    """
    # the local wind vector in the judging frame:
    jwind = st.att.inverse().transform_point(env.wind)  

    # the yaw rotation required to align the xz plane with the local wind vector:
    yaw_rotation = (jwind + st.vel).angles(
        st.att.inverse().transform_point(PX())
    ) * Point(0,0,1) 

    #transform the data by this yaw rotation:
    int_axis = convert_state(st, yaw_rotation)

    #the local wind vector in the intermediate frame:
    intwind = int_axis.att.inverse().transform_point(env.wind) 

    #the pitch rotation required to align the xy plane with the local wind vector:
    pitch_rotation = (intwind + int_axis.vel).angles(
        int_axis.att.inverse().transform_point(PX())
    ) * Point(0,1,0)

    #transform by this pitch rotation to get the wind axis state
    wind_axis =convert_state(int_axis, pitch_rotation)

    return wind_axis


def wind_to_body(st: State, flow: Flow):

    stability_axis = convert_state(stability_axis, -Point(0,0,1) * flow.beta)
    body_axis = convert_state(st, Point(0,1,0) * flow.alpha)

    return body_axis
