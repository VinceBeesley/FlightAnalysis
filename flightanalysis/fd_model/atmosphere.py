import numpy as np
import pandas as pd
from geometry.factory import geoms_factory, geom_factory

R = 287.058
GAMMA = 1.4

def get_rho(pressure, temperature):
    return pressure / (R * temperature)

names = ["pressure", "temperature"]

Atmosphere = geom_factory("Atmosphere", names)
Atmospheres = geoms_factory("Atmospheres", names, Atmosphere)
