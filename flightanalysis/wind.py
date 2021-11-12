import numpy as np
import pandas as pd
from scipy.optimize import minimize, rosen
from geometry import Point, Points


def wind_speed(h, v0, h0=300.0, a=0.2):
    return v0 * (h/h0)**a


def wind_vector(head, h, v0, h0=300.0, a=0.2):
    speed = wind_speed(h, v0, h0, a)
    try:
        return np.array([speed * np.cos(head), speed * np.sin(head), np.zeros(len(h))])
    except TypeError:
        return np.array([speed * np.cos(head), speed * np.sin(head), 0])



