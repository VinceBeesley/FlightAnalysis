import numpy as np
from geometry import Point, Points
from scipy.interpolate import interp1d
from flightanalysis import Section, get_q


def wind_vector(wind_speed_model, height, heading):
    """create a Point or Points representing the wind vector based on a wind speed model"""
    speed = wind_speed_model(height)
    direc =  Point(np.cos(heading), np.sin(heading), 0.0)
    
    if type(height) in [list, np.ndarray]:
        return Points.full(direc, len(speed)) * speed
    else:
        return direc * float(speed)




def uniform_wind_builder(args):
    """generates a wind function for constant wind
    
    Args:
        args ([float]): [heading, speed, exponent]

    Returns:
        function: function to get wind vector for given altitude and time. 
    """
    assert len(args) == 2
    return lambda height, time: wind_vector(
            lambda h: np.full(len(h), args[1]),
            height, args[0]
        )


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
# the best wind model variables will make cl vs alpha be the closest to a line

# 

def get_wind_error(args: np.ndarray, wind_builder, body: Section, judge: Section) -> float:
    wind_model = wind_builder(args)

    wind_vectors = wind_model(judge.gpos.z, np.zeros(len(judge.data)))

    wind = judge.judging_to_wind(wind_vectors)

    alpha, beta = body.measure_aoa(wind)

    airspeed = wind.measure_airspeed(wind_vectors)

    wind_force_coeff = wind.measure_coefficients(4.5, get_q(1.225, airspeed.x), 0.6 )

    long = np.array([alpha, wind_force_coeff.z])
    lat = np.array([beta, wind_force_coeff.y])

    a = 4 - np.sum(np.abs(np.corrcoef(long)))
    b = 4 - np.sum(np.abs(np.corrcoef(lat)))
    return a + b


