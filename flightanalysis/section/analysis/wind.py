import numpy as np
import pandas as pd
from scipy.optimize import minimize
from geometry import Point, Points
from flightanalysis import Section


def wind_speed(h, v0, h0=300.0, a=0.2):
    return v0 * (h/h0)**a


def wind_vector(head, h, v0, h0=300.0, a=0.2):
    speed = wind_speed(h, v0, h0, a)
    try:
        return np.array([speed * np.cos(head), speed * np.sin(head), np.zeros(len(h))])
    except TypeError:
        return np.array([speed * np.cos(head), speed * np.sin(head), 0])



def get_wind_error(args: np.ndarray, sec: Section) -> float:
    #wind vectors at the local positions
    local_wind = Points(wind_vector(head=args[0], h=np.maximum(sec.gpos.z, 0), v0=args[1], a=args[2]).T)

    #wind vectors in body frame
    body_wind = sec.gatt.inverse().transform_point(local_wind)

    #body frame velocity - wind vector should be wind axis velocity
    #error in wind axis velocity, is the non x axis part (because we fly forwards)
    air_vec_error = (sec.gbvel - body_wind) * Point(0,1,1)

    #but the wind is only horizontal, so transform to world frame and remove the z component
    world_air_vec_error = sec.gatt.transform_point(air_vec_error) * Point(1,1,0)

    #the cost is the cumulative error
    return sum(abs(world_air_vec_error))



def calculate_winds(sec: Section):
    res = minimize(get_wind_error, [np.pi, 5.0, 0.2], args=sec, method = 'Nelder-Mead')

    if res.x[1] < 0:
        res.x[1] = -res.x[1]
        res.x[0] = (res.x[0] + np.pi) % (2 * np.pi) 
    
    world_wind = Points(wind_vector(
        head=res.x[0], 
        h=np.maximum(sec.pos.z, 0), 
        v0=res.x[1], 
        a=res.x[2]
    ))

    body_wind = sec.gatt.inverse().transform_point(world_wind)

    return pd.concat(
        [world_wind.to_pandas(prefix="wv", index=sec.data.index),
        body_wind.to_pandas(prefix="bwv", index=sec.data.index),
        ]
    )
