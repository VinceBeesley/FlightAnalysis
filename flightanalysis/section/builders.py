import numpy as np
from . import Section, State
from geometry import Points, Quaternions


def extrapolate_state(istate: State, duration: float, freq: float = None):
    t = Section.t_array(duration, freq)

    bvel = Points.from_point(istate.bvel, len(t))

    return Section.from_constructs(
        t,
        pos = Points.from_point(istate.pos,len(t)) + istate.transform.rotate(bvel) * t,
        att = Quaternions.from_quaternion(istate.att, len(t)),
        bvel = bvel,
        brvel=Points(np.zeros((len(t), 3))),
        bacc=Points(np.zeros((len(t), 3)))
    )
