

from flightanalysis.schedule.elements import Line
import unittest
from geometry import Transformation, Point, Quaternion, PX, Euler, P0
import numpy as np
from pytest import approx



def test_create_template():
    template = Line(30, 100).create_template(Transformation())
    
    np.testing.assert_array_almost_equal(
        template[-1].pos.data,
        PX(100).data,
        0
    )
  

def test_match_intention():
    # fly a line 20 degrees off the X axis for 100m, with 1 roll to the left
    flown = Line(30, 100, -2*np.pi).create_template(Transformation(
            Point(-100, 200, 300),
            Euler(np.pi, np.radians(20), 0)
        ))

    # but it was meant to be along the X axis.
    new_el = Line(30, 100, 2 * np.pi).match_intention(
        Transformation(P0(), Euler(np.pi, 0, 0)),
        flown)

    # only amount of length in the intended direction is counted
    assert new_el.length == approx(100,1e-3)

    # roll direction should match
    assert np.sign(new_el.roll) == np.sign(np.mean(Point(flown.rvel).x))


def test_from_roll():
    roll = Line.from_roll(30, 1, 2 * np.pi)
    assert roll.rate == 1
    assert roll.length == 30 * 2 * np.pi