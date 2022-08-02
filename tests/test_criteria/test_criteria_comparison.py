from flightanalysis.criteria.comparison import f3a_radius
import numpy as np


def test_lookup():
    assert f3a_radius.lookup(1.1) == 0.0
    assert f3a_radius.lookup(1.8) == 1.5
    assert f3a_radius.lookup(3.5) == 2.5


def test_compare():
    assert f3a_radius.compare(1, 1.1) == 0.0
    assert f3a_radius.compare(1.6, 1) == 1.0
    assert f3a_radius.compare(1, 3.2) == 2.5


def test_call():
    np.testing.assert_array_equal(f3a_radius(1,2,4), [0, 2, 2])