import numpy as np
import unittest
from flightanalysis.schedule.element import Loop, Line, Snap, Spin, StallTurn, El
from geometry import Transformation, Points, Point, Quaternion


class TestLoop(unittest.TestCase):
    def test_create_template(self):
        elm = Loop(1.0, 0.5, 0.5, False).scale(100.0)

        new_elm = elm.create_template(Transformation(), 30.0)

        np.testing.assert_array_almost_equal(
            new_elm.get_state_from_index(-1).pos.to_list(),
            [0.0, 0.0, 100.0]
        )

    def test_match_axis_rate(self):
        elm = Loop(0.5, 0.5, 0.0, False).scale(
            100.0
        ).match_axis_rate(
            1.0, 30.0
        ).create_template(Transformation(), 30.0)
        self.assertAlmostEqual(
            abs(Points.from_pandas(elm.brvel).y.mean()), 1.0)

        elm = Loop(0.5, -0.5, 0.0, False).scale(
            100.0
        ).match_axis_rate(
            1.0, 30.0
        ).create_template(Transformation(), 30.0)
        self.assertAlmostEqual(
            abs(Points.from_pandas(elm.brvel).y.mean()), 1.0)

    def test_match_intention(self):
        elm = Loop(1.0, 0.5, 0.5, False)

        #simulate an uncorrected 5 degree roll error
        flown = elm.scale(100.0).create_template(Transformation(
            Point(1.0, 0.0, 0.0),
            Quaternion.from_euler(Point(np.radians(5.0), 0.0, 0.0))
        ),30.0)

        intention = elm.match_intention(Transformation(), flown)

        self.assertLess(intention.diameter, 100.0)
        
    def test_to_from_dict(self):
        el = Loop(1.0, 0.5, 0.5, False)
        dic = el.to_dict()
        tp = dic.pop("type")
        el2 = Loop(**dic)
        assert el.rolls == el2.rolls


class TestLine(unittest.TestCase):
    def test_create_template(self):
        elm = Line(0.5, 0.5).scale(100.0)
        template = elm.create_template(Transformation(), 30.0)
        np.testing.assert_array_almost_equal(
            template.get_state_from_index(-1).pos.to_list(),
            [50.0, 0.0, 0.0]
        )

    def test_match_axis_rate(self):
        elm = Line(0.5, 0.5).scale(100.0).match_axis_rate(
            1.0, 30.0).create_template(Transformation(), 30.0)
        self.assertAlmostEqual(elm.data.brvr.mean(), 1.0)

        elm = Line(0.5, -0.5).scale(100.0).match_axis_rate(
            1.0, 30.0).create_template(Transformation(), 30.0)
        self.assertAlmostEqual(abs(elm.data.brvr.mean()), 1.0)

    def test_match_intention(self):
        # fly a line 20 degrees off the X axis for 100m, with 1 roll
        flown = Line(1.0, -1.0).scale(
            100.0).create_template(Transformation(
                Point(1.0, 0.0, 0.0),
                Quaternion.from_euler(Point(0.0, np.radians(20.0), 0.0))
            ), 30.0)

        # but it was meant to be along the X axis.
        new_el = Line(1.0, 1.0).match_intention(
            Transformation(),
            flown)

        # only amount of length in the intended direction is counted
        self.assertAlmostEqual(new_el.length, 100 * np.cos(np.radians(20.0)))

        # roll direction should match
        self.assertEqual(
            np.sign(new_el.rolls), 
            np.sign(np.mean(Points.from_pandas(flown.brvel).x))
        )


class TestSnap(unittest.TestCase):
    def test_create_template(self):
        raw_el = Snap(1.0)
        template = raw_el.scale(
            150.0).create_template(Transformation(), 30.0)
        np.testing.assert_array_almost_equal(
            template.get_state_from_index(-1).pos.to_list(),
            [27, 0.0, 0.0]
        )
        self.assertEqual(len(raw_el.get_data(template).data),
                         len(template.data))


    

class TestStallTurn(unittest.TestCase):
    def test_create_template(self):
        template = StallTurn(1, 1).scale(
            150.0).create_template(Transformation(), 30.0)
        np.testing.assert_array_almost_equal(
            template.get_state_from_index(-1).pos.to_list(),
            [0.0, 1.0, 0]
        )

    def test_match_axis_rate(self):
        template = StallTurn(
            1, 1
        ).scale(
            150.0
        ).match_axis_rate(
            15.0, 30.0
        ).create_template(Transformation(), 30.0)
        self.assertAlmostEqual(template.data.brvy.mean(), 15.0)


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
