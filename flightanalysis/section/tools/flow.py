import numpy as np
import pandas as pd
from flightanalysis.section import Section
from geometry import Points
from flightanalysis.fd_model.freestream import FreeStreams, get_q
from flightanalysis.fd_model.atmosphere import get_rho
import warnings


def calculate_flow(self: Section) -> FreeStreams:
    if not "bwind" in self.existing_constructs():
        warnings.warn("Section does not contain wind estimation, assuming 0 wind")
        arspd =  self.gbvel
    else:
        arspd =  self.gbvel - self.gbwind

    return FreeStreams(
        np.array([
            np.arctan2(arspd.z, arspd.x), 
            np.arctan2(arspd.y, arspd.x),
            get_q(get_rho(self.pressure, self.temperature), abs(arspd) )
        ]).T,
    )
    

def append_flow(self: Section):
    if not "bwind" in self.existing_constructs():
        self = self.append_wind()
    return self.copy(flow = calculate_flow(self))

