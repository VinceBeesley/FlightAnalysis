import numpy as np
import pandas as pd
from flightanalysis.section import Section
from geometry import Points


def fd_prerequisites(func):
    def wrapper(self: Section, *args, **kwargs):
        if not "bwind" in self.existing_constructs():
            self = self.append_wind()
        return func(self, *args, **kwargs)
    return wrapper


@fd_prerequisites
def calculate_airspeed(self: Section) -> pd.DataFrame:
    return self.gbvel - self.gbwind

@fd_prerequisites
def append_wind(self: Section) -> Section:
    return self.append_columns(calculate_airspeed(self))

@fd_prerequisites
def calculate_aoa(self: Section) -> pd.DataFrame:
    bvel = self.gbvel - self.gbwind

    df = pd.DataFrame(
        np.array([np.arctan2(bvel.z, bvel.x), np.arctan2(bvel.y, bvel.x)]).T,
        columns=["alpha", "beta"]
        )
    df.index =self.data.index
    return df


@fd_prerequisites
def append_aoa(self: Section):
    alpha_beta = calculate_aoa(self)
    return self.append_columns(alpha_beta)

