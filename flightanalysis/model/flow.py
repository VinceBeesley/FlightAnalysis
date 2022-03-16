
from flightanalysis.base import Period, make_dt, make_error, default_vars
from typing import Union
from flightdata import Flight, Fields
from pathlib import Path
from flightanalysis.base.constructs import Constructs, SVar
from flightanalysis.section import Section
from flightanalysis.environment import Environments
from geometry import Point, Quaternion, Quaternions, Points
import numpy as np


flowvars = Constructs(dict(**default_vars, **{
    "aoa":   SVar(["alpha", "beta"],   np.array,   np.array,    make_error),
    "q":     SVar(["q"],               np.array,   np.array,    make_error),
}))


class Flows(Period):
    _cols = flowvars

    @staticmethod
    def build(body: Section, envs: Environments):
        judge = body.to_judging()
        wind = judge.judging_to_wind(envs.gwind)
        airspeed = wind.measure_airspeed(envs.gwind)
        alpha,beta = body.measure_aoa(wind)
        return Flows.from_constructs(
            body.gtime, 
            aoa=np.stack([alpha,beta]).T, 
            q=0.5 * 1.225 * airspeed.x
        )


class Flow(Period):
    _cols = flowvars
    Period = Flows

Flows.Instant = Flow

