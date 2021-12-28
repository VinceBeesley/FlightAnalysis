"""
The environment represents the wind vector, pressure and temperature.
The wind vector may vary in time and with altitude. Pressure and temperature are assumed constant

The Environment class contains the environment model and methods to build it

"""

import numpy as np
import pandas as pd
from flightanalysis import Section


class Environment:
    def __init__(self, pressure, temperature, wind: callable):
        self.pressure = pressure
        self.temperature = temperature
        self.wind = wind

    def __call__(self, altitude, time):
        return self.predictor(altitude, time)

    @staticmethod
    def fit_profile(sec: Section, wind_model):
        pass
