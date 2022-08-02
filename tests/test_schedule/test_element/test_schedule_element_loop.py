

from flightanalysis.schedule.elements import Loop
from pytest import approx, fixture

from geometry import Transformation, Point, Quaternion, PZ, PX, Euler
import numpy as np


@fixture
def half_loop():
    return Loop(30, 50.0, np.pi, 0)


def test_create_template(half_loop):
    new_elm = half_loop.create_template(Transformation())

    np.testing.assert_array_almost_equal(
        new_elm[-1].pos.data,
        PZ(-50).data,
        0
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

