from flightanalysis import State, Box, Time
from flightdata import Flight
from pytest import approx, mark
from geometry import Transformation, PX, PY, P0, Point
from geometry.testing import assert_almost_equal
import numpy as np
import pandas as pd
from ..conftest import box, flight
from .conftest import state
from time import sleep, time
from json import load


def test_extrapolate():
    initial = State.from_transform(
        Transformation(),
        vel=PX(30)
    )

    extrapolated = initial.extrapolate(10)
    assert extrapolated.x[-1] == approx(300)
    
    assert len(extrapolated) == 300
    assert_almost_equal(extrapolated.pos[0], initial.pos)


def test_extrapolate_rot():
    initial = State.from_transform(
        Transformation(),
        vel=PX(30),
        rvel=PY(2*np.pi/10)
    )

    extrapolated = initial.extrapolate(10)
    
    assert_almost_equal(
        extrapolated.pos[-2], 
        P0(),
        0
    )
    


def test_from_flight(flight, state):
    assert len(state.data) == len(flight.data)
    assert not np.any(np.isnan(state.pos.data))
    assert state.z.mean() > 0

def test_from_flight_pos(flight: Flight, state: State, box: Box):
    fl2 = flight.copy()
    fl2.primary_pos_source = 'position'
    st2 = State.from_flight(fl2, box)
    #pd.testing.assert_frame_equal(state.data, st2.data)
    assert all(st2.pos.z > 0)

def test_fc_json():
    with open('tests/data/manual_F3A_P23.json', 'r') as f:
        fcj = load(f)
    fl = Flight.from_fc_json(fcj)
    box = Box.from_fcjson_parmameters(fcj['parameters'])
    st = State.from_flight(fl, box)
    assert all(st.pos.z > 0)


def test_stack_singles():
    start=time()
    st=State.from_constructs(Time(time(), 0))
    
    for _ in range(10):
        sleep(0.01)
        st=st.append(State.from_constructs(Time.from_t(0)), "now")
        

    assert time()-start == approx(st.duration, abs=1e-2)

def test_fill():
    _t = Time.from_t(np.linspace(0, 1, 11))
    st0 = State.from_transform(Transformation.zero(), vel=PX(10))
    st = st0.fill(_t)
    assert len(st) == 11
    assert st.pos.x[0] == approx(0)
    assert st.pos.x[-1] == approx(10)
    
