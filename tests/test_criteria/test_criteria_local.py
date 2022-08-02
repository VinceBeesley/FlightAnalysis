from pytest import fixture
import numpy as np
from flightanalysis.criteria.local import Combination, angle_f3a, AngleCrit




def test_anglecrit_call():
    np.testing.assert_array_equal(
        angle_f3a(*list(np.radians([10, 1, 30]))),
        [1, 0, 2]
    )


@fixture
def combo():
    return Combination(
        [[0, np.pi, 0, -np.pi], [0, -np.pi, 0, np.pi]],
        angle_f3a
    )


def test_combination_getitem(combo):
    np.testing.assert_array_equal(combo[0], [0, np.pi, 0, -np.pi])

def test_combination_check_option(combo):
    assert combo.check_option(0, -np.pi, 0, np.pi) == 1

def test_get_option_error(combo):
    np.testing.assert_array_almost_equal(
        np.degrees(combo.get_option_error(1, *list(np.radians([10, -185, 5, 182])))), 
        [10, -5, 5, 2]
    )


def test_combination_call(combo):
    np.testing.assert_array_equal(
        combo(*list(np.radians([10, -185, 5, 182]))), 
        [1, 0.5, 0.5, 0]
    )
     