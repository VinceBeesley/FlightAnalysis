

from flightanalysis.schedule.elements import Loop, El
from pytest import approx, fixture, mark
from flightanalysis import State
from geometry import Transformation, Point, Quaternion, PZ, PX, Euler, P0
import numpy as np
from geometry.testing import assert_almost_equal, assert_equal
import json 


@fixture
def half_loop():
    return Loop(30, 50.0, np.pi, 0)

@fixture
def hl_template(half_loop):
    return half_loop.create_template(State.from_transform(Transformation(), vel=PX(30)))


def test_create_template_final_position(half_loop, hl_template):
    assert_almost_equal(
        hl_template[-1].pos,
        PZ(-half_loop.diameter),
        2
    )

def test_create_template_final_attitude(half_loop, hl_template):
    assert_almost_equal(
        hl_template[-1].att.transform_point(PX(1)),
        PX(-1)
    )


def test_match_intention():

    el = Loop(30, 100, np.radians(180), np.pi, False)

    tp = el.create_template(State.from_transform(Transformation(),vel=PX(30))) 

    att = Euler(0, np.radians(20), 0)

    fl = el.create_template(State.from_transform(
        Transformation(P0(), att),
        vel=att.inverse().transform_point(PX(30))
    ))

    el_diff = Loop(20, 50, np.radians(180), -np.pi, False)


    el2 = el_diff.match_intention(tp[0].transform, fl)

    assert el == el2

def test_match_intention_ke():

    el = Loop(30, 100, np.radians(180), np.pi, True)

    tp = el.create_template(State.from_transform(Transformation(),vel=PX(30))) 

    att = Euler(0, np.radians(20), 0)

    fl = el.create_template(State.from_transform(
        Transformation(P0(), att),
        vel=att.inverse().transform_point(PX(30))
    ))

    el_diff = Loop(20, 50, np.radians(180), -np.pi, True)


    el2 = el_diff.match_intention(tp[0].transform, fl)

    assert el == el2
    
    assert np.isclose(el2.rate, fl.p.mean(), 0.01)


@fixture
def th_e0()->State:
    return State.from_csv("tests/test_schedule/test_element/p23_th_e0.csv")

@fixture
def th_el()->Loop:
    with open("tests/test_schedule/test_element/p23_th_e0.json", "r") as f:
        return El.from_dict(json.load(f))

@fixture
def th_e0_tp()->State:
    return State.from_csv("tests/test_schedule/test_element/p23_th_e0_template.csv")



@fixture
def ql():
    return Loop(30, 100, np.pi/2, 0)

@fixture
def ql_tp(ql):
    return ql.create_template(Transformation.zero())


@fixture
def ql_fl():
    return Loop(
        30, 
        100, 
        np.pi/2 - np.radians(10), 
        0
    ).create_template(Transformation.zero())

def test_intra_scoring(ql, ql_tp, ql_fl):
    ql_fl = ql.setup_analysis_state(ql_fl, ql_tp)
    ql_tp = ql.setup_analysis_state(ql_tp, ql_tp)
    dgs = ql.intra_scoring.apply(ql, ql_fl, ql_tp)

    pass
