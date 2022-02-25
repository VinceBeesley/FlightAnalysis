from .constructs import Constructs
from .period import Period
from .instant import Instant



import numpy as np


def make_dt(sec) -> np.array:
    return np.gradient(sec.data.index)


def make_error(sec):
    raise NotImplementedError("cant construct a section without time, pos and att data")
