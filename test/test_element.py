import numpy as np
import unittest
from flightanalysis.schedule.element import LoopEl, LineEl, SnapEl, SpinEl, StallTurnEl
from geometry import Transformation, Point, Quaternion

class TestElement(unittest.TestCase):
    def test_create_template(self):
        elm = LoopEl( 1.0,0.0,0.5)

        new_elm = elm.create_template(
            Transformation(Point(0.0, 0.0, 0.0), Quaternion.from_euler(Point(0.0, 0.0, 0.0))),
            30.0,
            100.0
        )

        np.testing.assert_array_almost_equal(
            new_elm.get_state_from_index(-1).pos.to_list(),
            [0.0, 0.0, 100.0]
        )