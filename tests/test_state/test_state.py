from flightanalysis.state.state import State
from flightanalysis.flightline import Box, FlightLine
from flightanalysis.base.table import Time
from geometry import Point, Quaternion, Transformation, PX
from flightdata import Flight, Fields
import numpy as np
import pandas as pd
from pytest import approx, fixture
from json import dumps, loads

flight = Flight.from_csv('tests/test_inputs/test_log_00000052_flight.csv')

df = pd.DataFrame(np.random.random((200,8)), columns=['t', 'x', 'y', 'z', 'rw', 'rx', 'ry', 'rz'])
df['t'] = np.linspace(0, 200/30, 200)
df = df.set_index("t", drop=False)


@fixture
def state():
    return State(df) 

def test_child_init(state):
    assert all([col in state.data.columns for col in state.constructs.cols()])

def test_child_getattr(state):

    assert isinstance(state.x, np.ndarray)
    assert isinstance(state.pos, Point)

    assert isinstance(state.att, Quaternion)

    
def test_child_getitem(state):
    st = state[20]
    assert len(st)==1

def test_from_constructs():
    st = State.from_constructs(
        time=Time(5,1/30), 
        pos=Point.zeros(), 
        att=Quaternion.from_euler(Point.zeros())
    )
    assert st.pos == Point.zeros()

def test_from_transform():
    st =State.from_transform(Transformation())
    assert st.vel.x == 0


    st =State.from_transform(Transformation(), vel=PX(20))
    assert st.vel.x == 20


def test_to_from_dict(state):
    st = state.label(manoeuvre="test")
    data_dict = st.to_dict()
    data_json = dumps(data_dict)
    data_new_dict = loads(data_json)
    st_new = State.from_dict(data_new_dict)
    assert st_new.duration == state.duration


@fixture
def labst():
    st=State.from_transform(Transformation.zero()).extrapolate(10)
    al = State.stack([st.label(element=f"test{i}") for i in range(5)])
    al.data.t = al.data.t + 100
    return al


def test_state_edit_labels_increase(labst):
    
    labst2=labst.edit_labels("element", "test3",  45)

    assert labst2.get_element("test3").duration == approx(15, abs=0.2)
    assert labst2.get_element("test4").duration == approx(5, abs=0.2)


def test_state_edit_labels_reduce(labst):
    labst2=labst.edit_labels("element", "test3",  35)

    assert labst2.get_element("test3").duration == approx(5, abs=0.2)
    assert labst2.get_element("test4").duration == approx(15, abs=0.2)


def test_state_edit_labels_end(labst):
    labst2=labst.edit_labels("element", "test3",  55)

    assert labst2.get_element("test3").duration == approx(20, abs=0.2)

    assert not "test4" in labst2.data.element.unique()