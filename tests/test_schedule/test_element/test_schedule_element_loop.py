

from flightanalysis.schedule.elements import Loop
from pytest import approx, fixture

from geometry import Transformation, Point, Quaternion, PZ, PX, Euler
import numpy as np
from geometry.testing import assert_almost_equal, assert_equal

@fixture
def half_loop():
    return Loop(30, 50.0, np.pi, 0)

@fixture
def hl_template(half_loop):
    return half_loop.create_template(Transformation())

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


def test_match_axis_rate(half_loop):
    elm = half_loop.match_axis_rate(1.0).create_template(Transformation())
    assert abs(elm.q.mean()) == approx(1, 1e-1)


def test_match_intention(half_loop):
    #simulate an uncorrected 5 degree roll error
    flown = half_loop.create_template(
        Transformation(PX(),Euler(np.radians(5.0), 0.0, 0.0))
    )

    intention = half_loop.match_intention(Transformation(), flown)

    assert intention.diameter < 100.0
    
def test_to_from_dict():
    el = Loop(30, 100, np.pi, np.pi, False)
    dic = el.to_dict()
    tp = dic.pop("type")
    el2 = Loop(**dic)
    assert el.roll == el2.roll

