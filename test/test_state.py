from flightanalysis.state import State, SVars
from flightanalysis.flightline import Box, FlightLine
import unittest
from geometry import Point, Quaternion
from flightdata import Flight, Fields
import numpy as np
import pandas as pd


flight = Flight.from_csv('test/P21.csv')


class TestSvars(unittest.TestCase):
    def test_columns(self):
        vars = SVars()
        self.assertEqual(len(vars.columns), 31)
        self.assertEqual(vars.pos, ['x', 'y', 'z'])
        self.assertEqual(vars[0], 'x')
        self.assertEqual(tuple(vars[:3]), tuple(list('xyz')))
        self.assertTrue('x' in vars)
        self.assertFalse('bra' in vars)


class TestState(unittest.TestCase):
    def test_classmethods(self):
        st = State(pd.Series({col: 0 for col in State.vars}))
        self.assertEqual(st.x, 0)

    def test_from_posattvel(self):
        # TODO this method needs to be reconsidered with the new columns.
        seq = State.from_posattvel(
            Point(50, 170, 150),
            Quaternion.from_euler(Point(0, 0, np.pi)),
            Point(30, 0, 0)
        )

        self.assertEqual(seq.x, 50)
        self.assertEqual(seq.rx, 0)
        self.assertEqual(seq.vx, 30)
        self.assertIsInstance(seq.pos, tuple)
        self.assertEqual(Point(*seq.pos).x, 50)

    def test_body_to_world(self):
        st = State.from_posattvel(
            Point(50, 170, 150),
            Quaternion.from_euler(Point(0, 0, np.pi)),
            Point(-30, 0, 0)
        )

        pt = st.body_to_world(Point(0, 1, 0))
        self.assertEqual(pt.x, 50)
        self.assertEqual(pt.y, 169)
        self.assertEqual(pt.z, 150)

    def test_cv_projection(self):
        st = State.from_posattvel(
            Point(50, 170, 150),
            Quaternion.from_euler(Point(0, 0, np.pi)),
            Point(-30, 0, 0)
        )
        cv = st.constant_velocity_projection(1)
        np.testing.assert_array_equal(cv.pos, [20, 170, 150])

    def test_cv_projection_radius(self):
        st = State.from_posattvel(
            Point(0, 0, 0),
            Quaternion.from_euler(Point(0, 0, 0)),
            Point(30, 0, 0)
        )
        # rotating at 90 deg /s about y
        st.data[State.vars.brvel] = list(Point(0, np.pi/2, 0))

        cv = st.constant_velocity_projection(1)
        np.assert_array_equal(cv.pos, [0, 0, 0])


