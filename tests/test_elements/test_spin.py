from flightanalysis.schedule.elements import Spin
import unittest
from geometry import Transformation, Points, Point, Quaternion
import numpy as np



class TestSpin(unittest.TestCase):
    def test_create_template(self):
        template = Spin(0.2, 1, 1).scale(
            100.0).create_template(Transformation(), 30.0)
        np.testing.assert_array_almost_equal(
            template.get_state_from_index(-1).pos.to_list(),
            [2.0, 0.0, -22]
        )

    def test_match_axis_rate(self):
        template = Spin(0.2, 1, 1).scale(
            100.0
        ).match_axis_rate(
            10.0, 30.0
        ).create_template(Transformation(), 30.0)
        self.assertAlmostEqual(template.data.iloc[-1].brvr, 10.0)
