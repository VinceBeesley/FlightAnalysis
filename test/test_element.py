import numpy as np
import unittest
from flightanalysis.schedule.element import LoopEl, LineEl, SnapEl, SpinEl, StallTurnEl
from geometry import Transformation, Points


class TestLoopEl(unittest.TestCase):
    def test_create_template(self):
        elm = LoopEl(1.0, 0.5, 0.5, False).scale(100.0)

        new_elm = elm.create_template(Transformation(), 30.0)

        np.testing.assert_array_almost_equal(
            new_elm.get_state_from_index(-1).pos.to_list(),
            [0.0, 0.0, 100.0]
        )

    def test_match_axis_rate(self):
        elm = LoopEl(0.5, 0.5, 0.0, False).scale(100.0)
        new_elm = elm.match_axis_rate(1.0, 30.0)
        template = new_elm.create_template(Transformation(), 30.0)
        self.assertAlmostEqual(
            abs(Points.from_pandas(template.brvel).y.mean()), 1.0)


class TestLineEl(unittest.TestCase):
    def test_create_template(self):
        elm = LineEl(0.5, 0.5).scale(100.0)
        template = elm.create_template(Transformation(), 30.0)
        np.testing.assert_array_almost_equal(
            template.get_state_from_index(-1).pos.to_list(),
            [50.0, 0.0, 0.0]
        )

    def test_match_axis_rate(self):
        elm = LineEl(0.5, 0.5).scale(100.0).match_axis_rate(
            1.0, 30.0).create_template(Transformation(), 30.0)
        self.assertAlmostEqual(elm.data.brvr.mean(), 1.0)


class TestSnapEl(unittest.TestCase):
    def test_create_template(self):
        raw_el = SnapEl(0.15, 1.0)
        template = raw_el.scale(
            150.0).create_template(Transformation(), 30.0)
        np.testing.assert_array_almost_equal(
            template.get_state_from_index(-1).pos.to_list(),
            [22.5, 0.0, 0.0]
        )
        self.assertEqual(len(raw_el.get_data(template).data),
                         len(template.data))

    def test_match_axis_rate(self):
        template = SnapEl(0.15, 1.0).scale(150.0).match_axis_rate(
            20.0, 30.0).create_template(Transformation(), 30.0)
        self.assertAlmostEqual(template.data.brvr.mean(), 20.0)
        np.testing.assert_array_almost_equal(
            template.get_state_from_index(-1).pos.to_list(),
            [9.424778, 0, 0]
        )


class TestStallTurnEl(unittest.TestCase):
    def test_create_template(self):
        template = StallTurnEl(1, 1).scale(
            150.0).create_template(Transformation(), 30.0)
        np.testing.assert_array_almost_equal(
            template.get_state_from_index(-1).pos.to_list(),
            [0.0, 1.0, 0]
        )

    def test_match_axis_rate(self):
        template = StallTurnEl(
            1, 1
        ).scale(
            150.0
        ).match_axis_rate(
            15.0, 30.0
        ).create_template(Transformation(), 30.0)
        self.assertAlmostEqual(template.data.brvy.mean(), 15.0)


class TestSpinEl(unittest.TestCase):
    def test_create_template(self):
        template = SpinEl(0.2, 1, 1).scale(
            100.0).create_template(Transformation(), 30.0)
        np.testing.assert_array_almost_equal(
            template.get_state_from_index(-1).pos.to_list(),
            [2.0, 0.0, -22]
        )

    def test_match_axis_rate(self):
        template = SpinEl(0.2, 1, 1).scale(
            100.0
        ).match_axis_rate(
            10.0, 30.0
        ).create_template(Transformation(), 30.0)
        self.assertAlmostEqual(template.data.iloc[-1].brvr, 10.0)

