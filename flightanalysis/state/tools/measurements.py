from flightanalysis.state import State
import numpy as np
from geometry import Point


def measure_aoa(st: State, other:State=None):
    alpha, beta =  np.arctan(st.vel.z/st.vel.x), np.arctan(st.vel.y/st.vel.x)
    if other is not None: 
        alpha =  alpha - np.arctan(other.gbvel.z/other.gbvel.x)
        beta = beta - np.arctan(other.gbvel.y/other.gbvel.x)        
    return alpha, beta


def measure_airspeed(st: State, wind_vectors: Point) -> np.ndarray:
    return st.vel - st.att.inverse().transform_point(wind_vectors)


def measure_coefficients(st: State, mass, q, S):
    return st.acc * mass / (q * S)


def direction(self):
    if self.back_transform.rotate(Point(1, 0, 0)).x > 0:
        return "right"
    else:
        return "left"
