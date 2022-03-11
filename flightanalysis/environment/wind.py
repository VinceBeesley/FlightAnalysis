import numpy as np
import pandas as pd
from geometry import Point, Points
from scipy.interpolate import interp1d
from flightanalysis import Section, get_q
from typing import Callable, List, Tuple
from scipy.optimize import minimize


class WindModel:
    def __init__(self, func, kind, args):
        self.func = func
        self.kind = kind
        self.args = args

    def __call__(self, height, time=None):
        return self.func(height, time if not time is None else np.zeros(len(height)))

    

class WindModelBuilder:
    def __init__(self, builder, defaults: List[float], bounds: List[Tuple[float]]):
        self.builder = builder
        self.defaults = defaults
        self.bounds = bounds

    def __call__(self, params):
        return self.builder(params)
    
    @staticmethod
    def uniform(minwind=0.1, maxwind=20.0):

        def uniform_wind_builder(args):
            """generates a wind function for constant wind
            
            Args:
                args ([float]): [heading, speed]

            Returns:
                function: function to get wind vector for given altitude and time. 
            """
            assert len(args) == 2
            return WindModel(
                lambda height, time: WindModelBuilder.wind_vector(
                    lambda h: np.full(len(h), args[1]),
                    height, args[0]
                ),
                "uniform",
                args
            )

        return WindModelBuilder(
            uniform_wind_builder,
            [0.0, 3.0],
            [(0.0, 4 * np.pi), (minwind, maxwind)]
        )

    @staticmethod
    def power_law(minwind=0.1, maxwind=20.0):

        def wind_power_law_builder(args):
            """generates a wind function based on a standard wind altitude power law model
            
            Args:
                args ([float]): [heading, speed, exponent]

            Returns:
                function: function to get wind vector for given altitude and time. 
            """
            assert len(args) == 3
            return WindModel(
                lambda height, time: WindModelBuilder.wind_vector(
                    lambda h: args[1] * (h/300)**args[2],
                    height, args[0]
                ),
                "power_law",
                args
            )

        return WindModelBuilder(
                wind_power_law_builder,
                [0.0, 3.0, 0.2],
                [(-np.pi, 3 * np.pi), (minwind, maxwind), (0.1, 0.6)]
            )
        

    @staticmethod
    def fit(minwind=0.1, maxwind=20.0, minh=0, maxh=500, npoints=10, **kwargs ):

        def wind_fit_builder(args):
            """generates a wind function based on a fit through arbitrary number of points. 

            Args:
                args ([float]): first index heading, rest are speeds up to 1000m
                kind (str): see scipy docs for kind: https://docs.scipy.org/doc/scipy/reference/reference/generated/scipy.interpolate.interp1d.html#scipy.interpolate.interp1d
                            linear, nearest, nearest-up, zero, slinear, quadratic, cubic, previous, or next. zero, slinear, quadratic and cubic 

            Returns:
                function: function to get wind vector for given altitude and time.
            """
            model = interp1d(
                x=np.linspace(minh,np.sqrt(maxh), len(args)-1) ** 2,
                y=args[1:], 
                **kwargs
            ) 
            return WindModel(
                lambda height, time: WindModelBuilder.wind_vector(model, height, args[0]),
                "fit",
                args
            )
            
        return WindModelBuilder(
            wind_fit_builder,
            [3.0 for _ in range(npoints)],
            [(minwind, maxwind) for _ in range(npoints)]
        )


    @staticmethod
    def wind_vector(wind_speed_model, height, heading):
        """create a Point or Points representing the wind vector based on a wind speed model"""
        speed = wind_speed_model(height)
        direc =  Point(np.cos(heading), np.sin(heading), 0.0)
        
        if type(height) in [list, np.ndarray]:
            return Points.full(direc, len(speed)) * speed
        else:
            return direc * float(speed)


def fit_wind(body_axis: Section, windbuilder: WindModelBuilder, bounds=False, **kwargs):

    body_axis = Section(body_axis.data.loc[body_axis.data.bvx > 10])

    if not "method" in kwargs:
        kwargs["method"] = "nelder-mead"
    
    judge_axis = body_axis.to_judging()
    
    def get_coef_data(wind_model):
        wind_vectors = wind_model(judge_axis.gpos.z, judge_axis.gt)
        wind_axis = judge_axis.judging_to_wind(wind_vectors)
        alpha, beta = np.degrees(body_axis.measure_aoa(wind_axis))
        
        coeffs = wind_axis.measure_coefficients(
            4.5, 
            0.5 * 1.225 * wind_axis.measure_airspeed(wind_vectors).x**2, 
            0.6
        )

        return pd.DataFrame(np.stack([alpha, beta, coeffs.z, coeffs.y]).T, columns=["alpha", "beta", "cz", "cy"])

    def lincheck(x,y):
        fit = np.polyfit(x, y, deg=1)
        pred = fit[1] + fit[0] * x
        return np.sum(np.abs(pred - y)) 

    def cost_fn(wind_guess):
        wind_model = windbuilder(wind_guess)
        res = get_coef_data(wind_model)

        return 100*(lincheck(res.alpha, res.cz))# + lincheck(res.beta, res.cy) )

    res = minimize(
        cost_fn, 
        windbuilder.defaults, 
        bounds=windbuilder.bounds if bounds else None,
        **kwargs
    )

    args = res.x
    args[0] = args[0] % (2 * np.pi)
    return windbuilder(args)
