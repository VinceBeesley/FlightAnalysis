from winreg import ExpandEnvironmentStrings
from flightanalysis.base import Period, make_dt, make_error
from typing import Union
from flightdata import Flight, Fields
from pathlib import Path
from flightanalysis.base.constructs import Constructs, SVar
from geometry import Point, Quaternion, Quaternions, Points
import numpy as np

R = 287.058
GAMMA = 1.4

def get_rho(pressure, temperature):
    return pressure / (R * temperature)

def sl_assumption(sec):
    return np.full((len(sec), 2), [101325, 288.15, get_rho(101325, 288.15)])


envvars = Constructs({
    "time":  SVar("t",   ["t"],                 float,      np.array,    make_error,    ""),
    "dt":    SVar("dt",  ["dt"],                float,      np.array,    make_dt,       ""),
    "atm":   SVar("atm", ["P", "T", "rho"],     np.array,   np.array,    sl_assumption, ""),
    "wind":  SVar("wind",["wvx", "wvy", "wvz"], Points,     Points,      lambda sec: Points.full(Point.zeros(), len(sec)),    ""),
})


class Environments(Period):
    _cols = envvars

    def from_flight(flight: Union[Flight, str], control_conversion):
        if isinstance(flight, str):
            flight = {
                ".csv": Flight.from_csv,
                ".BIN": Flight.from_log
            }[Path(flight).suffix](flight)
        t=flight.data.index



        return Environments.from_constructs(time=t)


class Environment(Period):
    _cols = envvars
    Period = Environments

Environments.Instant = Environment