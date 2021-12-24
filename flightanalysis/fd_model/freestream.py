import numpy as np
import pandas as pd
from geometry.factory import geoms_factory, geom_factory
from flightanalysis.fd_model.atmosphere import get_rho, Atmospheres, Atmosphere
from typing import Union

def get_q(rho, v):
    return 0.5 * rho * v**2

names = ["alpha", "beta", "q"]

FreeStream = geom_factory("FreeStream", names)
FreeStreams = geoms_factory("FreeStreams", names, FreeStream)


def airspeed(self, atm:Union[Atmospheres, Atmosphere]):
    return np.sqrt(2+self.q * get_rho(atm.pressure, atm.temperature) )


FreeStreams.airspeed = airspeed
FreeStream.airspeed = airspeed
