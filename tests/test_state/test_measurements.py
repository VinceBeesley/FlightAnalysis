from flightanalysis.state.state import State

from flightanalysis.state.tools.measurements import direction

from ..conftest import flight, box, st
from pytest import approx, fixture

import numpy as np


def test_direction(st):
    direcs = direction(st)
    assert isinstance(direcs, np.ndarray)



def test_measure_aoa(st):
    pass