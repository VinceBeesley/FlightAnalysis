from flightanalysis.state.state import State
from flightanalysis.state.tools.builders import extrapolate, from_flight
from pytest import approx, fixture, raises
from geometry import Transformation, PX, PY, P0
import numpy as np
from ..conftest import flight, box

def test_extrapolate_no_rot():
    initial = State.from_transform(
        Transformation(),
        vel=PX(30)
    )

    extrapolated = extrapolate(initial, 10)
    
    np.testing.assert_array_almost_equal(
        extrapolated[-1].pos.data, 
        (initial.pos + PX(30) * 10).data
    )
    


def test_extrapolate_rot():
    initial = State.from_transform(
        Transformation(),
        vel=PX(30),
        rvel=PY(2*np.pi/10)
    )

    extrapolated = extrapolate(initial, 10)
    
    np.testing.assert_array_almost_equal(
        extrapolated[-1].pos.data, 
        P0().data
    )
    

@fixture
def state(flight, box):
    return from_flight(flight, box)

def test_from_flight(flight, state):
    assert len(state.data) == len(flight.data)


