

from flightanalysis.schedule.elements import Line
import unittest
from geometry import Transformation, Point, Quaternion, PX
import numpy as np
from pytest import approx



def test_create_template():
    elm = Line(0.5, 0.5).scale(100.0)
    template = elm.create_template(Transformation(), 30.0)
    np.testing.assert_array_almost_equal(
        template[-1].pos.data,
        PX(50).data
    )

    


def test_match_axis_rate():
    elm = Line(0.5, 0.5).scale(100.0).match_axis_rate(
        1.0, 30.0).create_template(Transformation(), 30.0)

    assert elm.rvel.mean().x[0] == approx(1.0, 10)

    elm = Line(0.5, -0.5).scale(100.0).match_axis_rate(
        1.0, 30.0).create_template(Transformation(), 30.0)

    assert abs(elm.rvel.mean()[0]) == approx(1.0)

def test_match_intention():
    # fly a line 20 degrees off the X axis for 100m, with 1 roll
    flown = Line(1.0, -1.0).scale(
        100.0).create_template(Transformation(
            Point(1.0, 0.0, 0.0),
            Quaternion.from_euler(Point(0.0, np.radians(20.0), 0.0))
        ), 30.0)

    # but it was meant to be along the X axis.
    new_el = Line(1.0, 1.0).match_intention(
        Transformation(),
        flown)

    # only amount of length in the intended direction is counted
    assert new_el.length == approx(100 * np.cos(np.radians(20.0)))

    # roll direction should match
    assert np.sign(new_el.rolls) == np.sign(np.mean(Point(flown.rvel).x))