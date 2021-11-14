import numpy as np
import pandas as pd
from scipy.optimize import minimize
from geometry import Point, Points
from flightanalysis.section import Section
import warnings

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


class Wind:
    def __init__(self, heading, speed, a):
        self.heading = heading
        self.speed = speed
        self.a = a
    
    def __call__(self, h):
        return wind_vector(
                head=self.heading, 
                h=np.maximum(h, 0), 
                v0=self.speed, 
                a=self.a
            )
        

def calculate_wind(self: Section) -> Wind:
    res = minimize(get_wind_error, [np.pi, 5.0, 0.2], args=self.flying_only(), method = 'Nelder-Mead')

    if res.x[1] < 0:
        res.x[1] = -res.x[1]
        res.x[0] = (res.x[0] + np.pi) % (2 * np.pi) 

    return Wind(*res.x)


def append_wind(self: Section, force=False) -> Section:
    if "bwind" in self.existing_constructs() and not force:
        warnings.warn("This Section already contains wind data, to overwrite use force=True")
        return self
    wind = calculate_wind(self)
    
    world_wind = Points(wind(self.pos.z).T)

    body_wind = self.gatt.inverse().transform_point(world_wind)

    return self.copy(wind=world_wind, bwind=body_wind)

