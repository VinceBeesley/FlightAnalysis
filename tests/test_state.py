from flightanalysis.state import State, SVars
from flightanalysis.flightline import Box, FlightLine
import unittest
from geometry import Point, Quaternion
from flightdata import Flight, Fields
import numpy as np
import pandas as pd


flight = Flight.from_csv('tests/P21.csv')


class TestSvars(unittest.TestCase):
    def test_columns(self):
        vars = SVars()
        self.assertEqual(len(vars.columns), 16)
        self.assertEqual(vars.pos, ['x', 'y', 'z'])
        self.assertEqual(vars[0], 'x')
        self.assertEqual(tuple(vars[:3]), tuple(list('xyz')))
        self.assertTrue('x' in vars)
        self.assertFalse('bra' in vars)


class TestState(unittest.TestCase):

    def test_from_posattvel(self):
        # TODO this method needs to be reconsidered with the new columns.
        seq = State(
            Point(50, 170, 150),
            Quaternion.from_euler(Point(0, 0, np.pi)),
            Point(30, 0, 0)
        )

        np.testing.assert_array_equal(list(seq.pos), [50, 170, 150])
        np.testing.assert_array_equal(list(seq.bvel), [30, 0, 0])
        np.testing.assert_array_equal(list(seq.brvel), [0, 0, 0])

    def test_body_to_world(self):
        st = State(
            Point(50, 170, 150),
            Quaternion.from_euler(Point(0, 0, np.pi)),
            Point(-30, 0, 0)
        )

        pt = st.body_to_world(Point(0, 1, 0))
        self.assertEqual(pt.x, 50)
        self.assertEqual(pt.y, 169)
        self.assertEqual(pt.z, 150)


if __name__ == '__main__':
    unittest.main()