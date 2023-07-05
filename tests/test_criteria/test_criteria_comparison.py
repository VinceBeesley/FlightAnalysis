from flightanalysis.schedule.scoring.criteria import f3a
import numpy as np


def test_lookup():
    assert f3a.radius(1.1) == 0.0
    assert f3a.radius(1.8) == 1.5
    assert f3a.radius(3.5) == 2.5


def test_compare():
    assert f3a.inter_radius([1, 1.1]) == 0.0
    assert f3a.inter_radius([1, 1.1]) == 1.0
    assert f3a.inter_radius([1, 1.1]) == 2.5


