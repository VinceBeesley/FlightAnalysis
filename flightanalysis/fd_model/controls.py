import numpy as np
import pandas as pd
from geometry.factory import geoms_factory, geom_factory
<<<<<<< HEAD
    
=======
from typing import Union

>>>>>>> devb

names = ["throttle", "aileron", "elevator", "rudder", "flap"]

FreeStream = geom_factory("FreeStream", names)
FreeStreams = geoms_factory("FreeStreams", names, FreeStream)


def from_flaperon_df(data:pd.DataFrame):
    data = data.assign(aileron=(data.aileron_1 + data.aileron_2)/2)
    return FreeStreams.from_df(data)

