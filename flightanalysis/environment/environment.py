
from flightanalysis.base import Period, Instant, make_dt, make_error, default_vars
from typing import Union
from flightdata import Flight, Fields
from pathlib import Path
from flightanalysis.base.constructs import Constructs, SVar
from geometry import Point, Quaternion, Quaternions, Points
from flightanalysis.section import Section
import numpy as np
from .wind import WindModel

R = 287.058
GAMMA = 1.4

def get_rho(pressure, temperature):
    return pressure / (R * temperature)

def sl_assumption(sec):
    return np.full((len(sec), 2), [101325, 288.15, get_rho(101325, 288.15)])


envvars = Constructs(dict(**default_vars, **{
    "atm":   SVar(["P", "T", "rho"],     np.array,   np.array,    sl_assumption),
    "wind":  SVar(["wvx", "wvy", "wvz"], Points,     Points,      lambda sec: Points.full(Point.zeros(), len(sec))),
}))


class Environments(Period):
    _cols = envvars

    @staticmethod
    def build(flight: Flight, sec: Section, wmodel: WindModel):

        df = flight.read_fields(Fields.PRESSURE)
        df = df.assign(temperature_0=291.15)
        df = df.assign(rho=get_rho(df["pressure_0"], df["temperature_0"]))

        return Environments.from_constructs(
            time=sec.gtime,
            atm=df.to_numpy(),
            wind=wmodel(sec.gpos.z)
        )


class Environment(Instant):
    _cols = envvars
    Period = Environments

Environments.Instant = Environment