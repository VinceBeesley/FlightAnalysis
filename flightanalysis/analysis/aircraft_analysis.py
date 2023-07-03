"""This is an attempt to use the flight data to produce information about the aircraft. Just an idea of how things could be organised.

could one day be developed into parameter ID stuff. 

"""
from flightanalysis.state import State
from flightanalysis.environment import Environment, WindModelBuilder, WindModel, Air
from flightanalysis.controls import Controls
from flightanalysis.model import Coefficients, Flow, cold_draft, ACConstants
from flightanalysis.flightline import Box
import numpy as np
import pandas as pd


contents = {
    "body": State, 
    "wind": State,
    "judge": State,
    "control": Controls,
    "environment": Environment,
    "flow": Flow,
    "coeffs": Coefficients
}

class Analysis:
    def __init__(self, flight, data):
        self.flight= flight
        self.data = data

    def __getattr__(self, name):
        if name in self.data.keys():
            return self.data[name]
        for val in self.data.values():
            if hasattr(val, name):
                return getattr(val, name)
        
    @staticmethod
    def build(
        flight, 
        box: Box, 
        wmodel: WindModel, 
        consts: ACConstants,
        control_mapping: dict
    ):
        
        body = State.from_flight(flight, box)
        judge = body.to_judging()
        controls = Controls.build(flight, control_mapping)
        environment = Environment.build(flight, body, wmodel)
        flow = Flow.build(body, environment)

        wind = body.body_to_wind(flow)
        coeffs = Coefficients.build(wind, flow, consts)

        return Analysis(
            flight,
            data = dict(
                body=body,
                wind=wind,
                judge=judge,
                control=controls,
                environment=environment,
                flow=flow,
                coeffs=coeffs
            )
        )

    def __getitem__(self, sli):
        return Analysis(
            self.flight[sli],
            {key: value[sli] for key, value in self.data.items()}    
        )


    def to_df(self):
        return pd.concat([
            self.body.data, 
            self.control.data, 
            self.environment.data, 
            self.flow.data,
            self.coeffs.data
        ],axis=1)

    def to_csv(self, path:str):
        self.to_df().to_csv(path)


def fit_wind(body_axis: State, windbuilder: WindModelBuilder, bounds=False, **kwargs):
    from scipy.optimize import minimize

    body_axis = State(body_axis.data.loc[body_axis.vel.x > 10])

    if not "method" in kwargs:
        kwargs["method"] = "nelder-mead"
    
    judge_axis = body_axis.to_judging()
    
    def lincheck(x,y):
        fit = np.polyfit(x, y, deg=1)
        pred = fit[1] + fit[0] * x
        return np.sum(np.abs(pred - y)) 

    def cost_fn(wind_guess):
        wind_model = windbuilder(wind_guess)
        
        env = Environment.from_constructs(
            body_axis.time, 
            Air.iso_sea_level(len(body_axis)),
            wind_model(judge_axis.pos.z, judge_axis.time.t)
        )
        
        flow = Flow.build(body_axis, env)

        coeffs = Coefficients.build(body_axis, flow, cold_draft)  
        
        return 100*(lincheck(flow.alpha, coeffs.cz) + lincheck(flow.beta, coeffs.cy))  

    res = minimize(
        cost_fn, 
        windbuilder.defaults, 
        bounds=windbuilder.bounds if bounds else None,
        **kwargs
    )

    args = res.x
    if args[1] < 0:
        args[0] = args[0] + np.pi
        args[1] = -args[1]
    args[0] = args[0] % (2 * np.pi)
    return windbuilder(args)

