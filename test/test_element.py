import numpy as np
import unittest
from flightanalysis.schedule.element import Element, ElClass
from geometry import Transformation, Point, Quaternion

class TestElement(unittest.TestCase):
    def test_create_template(self):
        elm = Element(
            ElClass.LOOP,  
            1.0,
            0.0,
            0.5
        )

        end_pos = elm.create_template(
            Transformation(Point(0.0, 0.0, 0.0), Quaternion.from_euler(Point(0.0, 0.0, 0.0))),
            30.0,
            100.0
        )

        np.testing.assert_array_almost_equal(
            end_pos.translation.to_list(),
            [0.0, 0.0, 100.0]
        )