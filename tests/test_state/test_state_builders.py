from flightanalysis.state.state import State
from flightanalysis.flightline import Box
from flightanalysis.state.tools.builders import extrapolate, from_flight
from flightdata import Flight
from flightanalysis.base.table import Time
from pytest import approx, fixture, raises
from geometry import Transformation, PX, PY, P0, Point
import numpy as np
from ..conftest import flight, box
from time import sleep, time

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
    
    assert len(extrapolated) == 10*30-1


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
    

def test_extrapolate_first_point():
    initial = State.from_transform(
        Transformation(),
        vel=PX(30),
        rvel=PX(1)
    )
    extrapolated = initial.extrapolate(10)
    np.testing.assert_array_almost_equal(extrapolated[0].att.data, initial.att.data)
    np.testing.assert_array_almost_equal(extrapolated[0].pos.data, initial.pos.data)
    




@fixture
def state(flight, box):
    return from_flight(flight, box)

def test_from_flight(flight, state):
    assert len(state.data) == len(flight.data)


def test_stack_singles():
    start=time()
    st=State.from_constructs(Time(time(), 0))
    
    for _ in range(10):
        sleep(0.01)
        st=st.append(State.from_constructs(Time.from_t(0)), "now")
        

    assert time()-start == approx(st.duration, abs=1e-2)


def test_from_fl():
    fl = Flight.from_csv("tests/test_inputs/00000129.csv")
    st = State.from_flight(fl, Box.from_initial(fl))
    
    assert not np.any(np.isnan(st.pos.data))
