from flightanalysis import State, Box, Time
from flightdata import Flight
from pytest import approx, fixture, raises
from geometry import Transformation, PX, PY, P0, Point
from geometry.testing import assert_almost_equal
import numpy as np
from ..conftest import box, flight
from .conftest import state
from time import sleep, time


def test_extrapolate():
    initial = State.from_transform(
        Transformation(),
        vel=PX(30)
    )

    extrapolated = initial.extrapolate(10)
    assert extrapolated.x[-2] == approx(300)
    
    assert len(extrapolated) == 300


def test_extrapolate_rot():
    initial = State.from_transform(
        Transformation(),
        vel=PX(30),
        rvel=PY(2*np.pi/10)
    )

    extrapolated = initial.extrapolate(10)
    
    assert_almost_equal(
        extrapolated.pos[-2], 
        P0()
    )
    

def test_extrapolate_first_point():
    initial = State.from_transform(
        Transformation(),
        vel=PX(30),
        rvel=PX(1)
    )
    extrapolated = initial.extrapolate(10)
    assert_almost_equal(extrapolated.att[0], initial.att)
    assert_almost_equal(extrapolated.pos[0], initial.pos)
    

def test_from_flight(flight, state):
    assert len(state.data) == len(flight.data)
    assert not np.any(np.isnan(state.pos.data))
    assert state.z.mean() > 0

def test_stack_singles():
    start=time()
    st=State.from_constructs(Time(time(), 0))
    
    for _ in range(10):
        sleep(0.01)
        st=st.append(State.from_constructs(Time.from_t(0)), "now")
        

    assert time()-start == approx(st.duration, abs=1e-2)


