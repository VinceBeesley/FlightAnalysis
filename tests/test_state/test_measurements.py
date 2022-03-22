from flightanalysis.state.state import State

from flightanalysis.state.tools.measurements import direction

from ..conftest import flight, box
from pytest import approx, fixture

import numpy as np

@fixture
def sec(flight, box):
    return State.from_flight(flight, box)

def test_direction(sec):
    direcs = direction(sec)
    assert isinstance(direcs, np.ndarray)

    