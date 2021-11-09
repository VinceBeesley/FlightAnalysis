from flightanalysis.schedule.elements import Spin
import unittest
from geometry import Transformation, Points, Point, Quaternion
import numpy as np
from pytest import approx

def test_create_template():
    template = Spin(1).scale(
        100.0).create_template(Transformation(), 10.0)
    assert template[-1].pos.z < 0

    assert template[-1].att.transform_point(Point(0,0,1)).x== approx(1)

def test_match_axis_rate():
    template = Spin(1, 1).scale(100.0).match_axis_rate(10.0, 30.0).create_template(Transformation(), 30.0)
    
    assert template.gbrvel.x.max() == approx(10.0)
    #assert np.sqrt(np.abs(template.gbrvel.x).max() **2 + np.abs(template.gbrvel.z).max() ** 2) == approx(10.0)

