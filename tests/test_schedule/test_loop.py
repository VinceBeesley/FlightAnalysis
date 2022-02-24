

from flightanalysis.schedule.elements import Loop
import pytest
from geometry import Transformation, Points, Point, Quaternion
import numpy as np


def test_create_template():
    elm = Loop(1.0, 0.5, 0.5, False).scale(100.0)

    new_elm = elm.create_template(Transformation(), 30.0)

    np.testing.assert_array_almost_equal(
        new_elm[-1].pos.to_list(),
        [0.0, 0.0, 100.0]
    )

def test_match_axis_rate():
    elm = Loop(0.5, 0.5, 0.0, False).scale(
        100.0
    ).match_axis_rate(
        1.0, 30.0
    ).create_template(Transformation(), 30.0)
    pytest.approx(
        abs(Points.from_pandas(elm.brvel).y.mean()), 1.0)

    elm = Loop(0.5, -0.5, 0.0, False).scale(
        100.0
    ).match_axis_rate(
        1.0, 30.0
    ).create_template(Transformation(), 30.0)
    pytest.approx(
        abs(Points.from_pandas(elm.brvel).y.mean()), 1.0)

def test_match_intention():
    elm = Loop(1.0, 0.5, 0.5, False)

    #simulate an uncorrected 5 degree roll error
    flown = elm.scale(100.0).create_template(Transformation(
        Point(1.0, 0.0, 0.0),
        Quaternion.from_euler(Point(np.radians(5.0), 0.0, 0.0))
    ),30.0)

    intention = elm.match_intention(Transformation(), flown)

    assert intention.diameter < 100.0
    
def test_to_from_dict():
    el = Loop(1.0, 0.5, 0.5, False)
    dic = el.to_dict()
    tp = dic.pop("type")
    el2 = Loop(**dic)
    assert el.rolls == el2.rolls

