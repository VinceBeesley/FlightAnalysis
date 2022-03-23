
from flightanalysis.base.table import Table, Time, SVar
from typing import Union
from flightdata import Flight, Fields
from pathlib import Path
from flightanalysis.base.constructs import Constructs, SVar
from flightanalysis.state import State
from flightanalysis.environment import Environment
from geometry import Point, Quaternion, Base
import numpy as np


class Flw(Base):
    cols = ["alpha", "beta", "q"]


class Flow(Table):
    constructs = Table.constructs + Constructs(dict(
        flow = SVar(Flw, ["alpha", "beta", "q"], None)
    ))

    @staticmethod
    def build(body: State, envs: Flw):
        judge = body.to_judging()
        wind = judge.judging_to_wind(envs.gwind)
        airspeed = wind.measure_airspeed(envs.gwind)
        alpha,beta = body.measure_aoa(wind)
        return Flow.from_constructs(
            body.time, 
            Flw(np.stack([alpha,beta, 0.5 * envs.rho * airspeed.x**2]).T) 
        )


