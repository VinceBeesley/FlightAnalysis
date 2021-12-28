import numpy as np
from geometry import Point, Points
from scipy.interpolate import interp1d
from flightanalysis import Section


def wind_vector(wind_speed_model, height, heading):
    """create a Point or Points representing the wind vector based on a wind speed model"""
    speed = wind_speed_model(height)
    direc =  Point(np.cos(heading), np.sin(heading), 0.0)
    
    if type(height) in [list, np.ndarray]:
        return Points.full(direc, len(speed)) * speed
    else:
        return direc * float(speed)


def wind_power_law_builder(args):
    """generates a wind function based on a standard wind altitude power law model
    
    Args:
        args ([float]): [heading, speed, exponent]

    Returns:
        function: function to get wind vector for given altitude and time. 
    """
    assert len(args) == 3
    return lambda height, time: wind_vector(
            lambda h: args[1] * (h/300)**args[2],
            height, args[0]
        )
    

def wind_fit_builder(args, kind="linear"):
    """generates a wind function based on a fit through arbitrary number of points

    Args:
        args ([float]): first index heading, rest are speeds up to 1000m
        kind (str): see scipy docs for kind: https://docs.scipy.org/doc/scipy/reference/reference/generated/scipy.interpolate.interp1d.html#scipy.interpolate.interp1d
                    linear, nearest, nearest-up, zero, slinear, quadratic, cubic, previous, or next. zero, slinear, quadratic and cubic 

    Returns:
        function: function to get wind vector for given altitude and time.
    """
    model = interp1d(
        x=np.linspace(0,np.sqrt(1000), len(args)-1) ** 2,
        y=args[1:], 
        kind=kind
    ) 
    return lambda height, ttime: wind_vector(model, height, args[0])
    

#given: 
# Section in body frame
# Section in judging frame
# some wind model
# some assumptions about the a/c model: 
#   lift/ aspd**2 = a * alpha       ->       a = lift / (arspd**2 * alpha)
#   sf/ aspd**2 = b * beta          ->       b = sf / (arspd**2 * beta)
# the best wind model will have the smallest standard deviations of a and b


def get_wind_error(args: np.ndarray, wind_builder, body: Section, judge: Section) -> float:
    # TODO this is producing noncense at the moment.
    wind_model = wind_builder(args)

    wind_vectors = wind_model(judge.gpos.z, np.zeros(len(judge.data)))

    wind = judge.judging_to_wind(wind_vectors)

    alpha, beta = body.measure_aoa(wind)

    airspeed = abs(body.gbvel )

    a = body.baz / (airspeed**2 * alpha) 
    b = body.bay / (airspeed**2 * beta)

    return abs(a.var()) + abs(b.var())


