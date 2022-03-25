import numpy as np
import pandas as pd
from flightanalysis.state import State
from geometry import Point, Quaternion, Transformation, PX



def transform_state(st: State, transform: Transformation) -> State:
    return State.from_constructs(
        time=st.time,
        pos=transform.point(st.pos),
        att=transform.rotate(st.att),
        vel=transform.rotate(st.vel),
        rvel=transform.rotate(st.rvel),
        acc=transform.rotate(st.acc),
        racc=transform.rotate(st.racc),
    )

def superimpose_angles(st: State, angles: Point, reference:str="body"): 
    assert reference in ["body", "world"]
    sec =  State.from_constructs(
        st.time,
        st.pos,
        st.att.rotate(angles) if reference=="world" else st.att.body_rotate(angles)
    )

    if "sub_element" in st.data.columns:
        sec = sec.append_columns(st.data["sub_element"])
    return sec


def superimpose_rotation(st: State, axis: Point, angle: float, reference:str="body"):
    """Generate a new section, identical to st, but with a continous rotation integrated
    """
    t = st.time.t - st.time.t[0]
    rate = angle / st.time.t
    superimposed_rotation = t * rate

    angles = axis.unit().tile(len(t)) * superimposed_rotation

    return st.superimpose_angles(angles, reference)



def superimpose_roll(st: State, proportion: float) -> State:
    """Generate a new section, identical to st, but with a continous roll integrated

    Args:
        proportion (float): the amount of roll to integrate
    """
    return st.superimpose_rotation(PX(), 2 * np.pi * proportion)



def smooth_rotation(st: State, axis: Point, angle: float, reference:str="body", w: float=0.25, w2=0.1):
    """Accelerate for acc_prop * t, flat rate for middle, slow down for acc_prop * t.

    Args:
        axis (Point): Axis to rotate around.
        angle (float): angle to rotate.
        reference (str, optional): rotate about body or world. Defaults to "body".
        acc_prop (float, optional): proportion of total rotation to be accelerating for. Defaults to 0.1.
    """

    t = np.array(st.data.index) - st.data.index[0]

    T = t[-1]

    V = angle / (T*(1-0.5*w-0.5*w2))  # The maximum rate

    #between t=0 and t=wT
    x = t[t<=w*T]
    angles_0 = (V * x**2) / (2 * w * T)    

    #between t=wT and t=T(1-w)
    y=t[(t>w*T) & (t<=(T-w2*T))]
    angles_1 = V * y - V * w * T / 2
    
    #between t=T(1-w2) and t=T
    z = t[t>(T-w2*T)] - T + w2*T
    angles_2 = V*z - V * z **2 / (2*w2*T) + V*T - V * w2 * T  - 0.5*V*w*T

    angles = Point.from_point(axis.unit(), len(t)) * np.concatenate([angles_0, angles_1, angles_2])

    return st.superimpose_angles(angles, reference)


