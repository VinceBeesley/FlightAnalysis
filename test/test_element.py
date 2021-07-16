import numpy as np
import unittest
from flightanalysis.schedule.element import LoopEl, LineEl, SnapEl, SpinEl, StallTurnEl
from geometry import Transformation, Point, Quaternion

class TestLoopEl(unittest.TestCase):
    def test_create_template(self):
        elm = LoopEl( 0.5, 0.5, 0.0, False)

        new_elm = elm.create_template(Transformation(),30.0, 100.0)

        np.testing.assert_array_almost_equal(
            new_elm.get_state_from_index(-1).pos.to_list(),
            [0.0, 0.0, 50.0]
        )

    def test_match_axis_rate(self):
        elm = LoopEl( 0.5, 0.5, 0.0, False)
        new_elm = elm.match_pitch_rate()