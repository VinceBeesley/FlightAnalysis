

from flightanalysis.elements import Line
import unittest
from geometry import Transformation, Point, Quaternion, PX, Euler, P0
import numpy as np
from pytest import approx
from flightdata import State


def test_create_template():
    template = Line(30, 100).create_template(State.from_transform(Transformation(),vel=PX(30)))
    
    np.testing.assert_array_almost_equal(
        template[-1].pos.data,
        PX(100).data,
        0
    )
  

def test_from_roll():
    roll = Line.from_roll(30, 1, 2 * np.pi)
    assert roll.rate == 1
    assert roll.length == 30 * 2 * np.pi


def test_match_intention():
    # a line
    el = Line(30, 100, np.radians(180), "test")

    # a template State
    tp = el.create_template(State.from_transform(Transformation(),vel=PX(30)))

    # some alpha
    att = Euler(0, np.radians(20), 0)

    # a flown State
    fl = el.create_template(
        State.from_transform(
            Transformation(P0(), att),
            vel=att.inverse().transform_point(PX(30))
    ))

    # a slightly different line
    el2 = Line(15, 200, -np.radians(180), "test")

    #match intention should make it the same as the first line
    el3 = el2.match_intention(tp[0].transform, fl)
    assert el3 == el

