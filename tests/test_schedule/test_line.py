

from flightanalysis.schedule.elements import Line
import unittest
from geometry import Transformation, Point, Quaternion, PX, Euler
import numpy as np
from pytest import approx



def test_create_template():
    template = Line(30, 100, 0).create_template(Transformation())
    
    np.testing.assert_array_almost_equal(
        template[-1].pos.data,
        PX(100).data
    )
  

def test_match_axis_rate():
    elm = Line(30, 50, np.pi).match_axis_rate(
        1.0).create_template(Transformation())

    assert elm.rvel.mean().x[0] == approx(1.0, 10)

    elm = Line(30, 50, -np.pi).scale(100.0).match_axis_rate(
        1.0).create_template(Transformation())

    assert abs(elm.rvel.mean()[0]) == approx(1.0)

def test_match_intention():
    # fly a line 20 degrees off the X axis for 100m, with 1 roll to the left
    flown = Line(30, 100, -2*np.pi).create_template(Transformation(
            PX(),
            Euler(0.0, np.radians(20.0), 0.0)
        ))

    # but it was meant to be along the X axis.
    new_el = Line(30, 100, 2 * np.pi).match_intention(
        Transformation(),
        flown)

    # only amount of length in the intended direction is counted
    assert new_el.length == approx(100 * np.cos(np.radians(20.0)), 1)

    # roll direction should match
    assert np.sign(new_el.roll) == np.sign(np.mean(Point(flown.rvel).x))


def test_from_roll():
    roll = Line.from_roll(30, 1, 2 * np.pi)
    assert roll.rate == 1
    assert roll.length == 30 * 2 * np.pi