import numpy as np
import pandas as pd
from geometry.factory import geoms_factory, geom_factory

def get_q(rho, v):
    return 0.5 * rho * v**2

names = ["alpha", "beta", "q"]

FreeStream = geom_factory("FreeStream", names)
FreeStreams = geoms_factory("FreeStreams", names, FreeStream)
