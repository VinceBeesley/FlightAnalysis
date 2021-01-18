from flightanalysis.state import State
from flightanalysis.flightline import Box, FlightLine
import unittest
from geometry import Point, Quaternion
from flightdata import Flight, Fields
import numpy as np
import pandas as pd


flight = Flight.from_csv('test/P21.csv')


class TestState(unittest.TestCase):
    def test_from_posattvel(self):
        seq = State.from_posattvel(
            Point(50, 170, 150),
            Quaternion.from_euler(Point(0, 0, np.pi)),
            Point(30, 0, 0)
        )

        self.assertEqual(seq.x, 50)
        self.assertEqual(seq.rx, 0)
        self.assertEqual(seq.dx, -30)
        self.assertIsInstance(seq.pos, tuple)
        self.assertEqual(Point(*seq.pos).x, 50)

    def test_body_to_world(self):
        st = State.from_posattvel(
            Point(50, 170, 150),
            Quaternion.from_euler(Point(0, 0, np.pi)),
            Point(-30, 0, 0)
        )

        pt = st.body_to_world(Point(0,1,0))
        self.assertEqual(pt.x, 50)
        self.assertEqual(pt.y, 169)
        self.assertEqual(pt.z, 150)