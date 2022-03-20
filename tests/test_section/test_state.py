from flightanalysis.state.state import State
from flightanalysis.flightline import Box, FlightLine
import unittest
from geometry import Point, Quaternion, Transformation
from flightdata import Flight, Fields
import numpy as np
import pandas as pd
from pytest import approx, fixture

flight = Flight.from_csv('tests/test_inputs/test_log_00000052_flight.csv')

df = pd.DataFrame(np.random.random((200,8)), columns=['t', 'x', 'y', 'z', 'rw', 'rx', 'ry', 'rz'])
df['t'] = np.linspace(0, 200/30, 200)
df = df.set_index("t", drop=False)


@fixture
def state():
    return State(df) 

def test_child_init(state):
    assert all([col in state.data.columns for col in state.cols.cols])

def test_child_getattr(state):

    assert isinstance(state.x, np.ndarray)
    assert isinstance(state.pos, Point)

    assert isinstance(state.att, Quaternion)

    
def test_child_getitem(state):
    st = state[20]
    assert len(st)==1




def test_from_constructs():
    st = State.from_constructs(time=5, pos=Point.zeros(), att=Quaternion.from_euler(Point.zeros()))
    assert st.transform.translation == Point.zeros()

def test_from_transform():
    st =State.from_transform(Transformation(),bvel=Point(30, 0, 0))
    assert st.bvel.x == 30


    