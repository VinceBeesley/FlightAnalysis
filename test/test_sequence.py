from flightanalysis.sequence import Sequence
from flightanalysis.flightline import Box, FlightLine
import unittest
from geometry import Point, Quaternion
from flightdata import Flight, Fields
import numpy as np
import pandas as pd


flight = Flight.from_csv('test/P21.csv')


class TestSequence(unittest.TestCase):
    def test_from_flight(self):
        seq = Sequence.from_flight(
            flight, FlightLine.from_initial_position(flight))
        self.assertIsInstance(seq.x, pd.Series)
        self.assertIsInstance(seq.y, pd.Series)
        self.assertIsInstance(seq.z, pd.Series)
        self.assertIsInstance(seq.rw, pd.Series)
        self.assertIsInstance(seq.rx, pd.Series)
        self.assertIsInstance(seq.ry, pd.Series)
        self.assertIsInstance(seq.rz, pd.Series)
        self.assertGreater(seq.z.mean(), 0)

    def test_from_position(self):
        seq = Sequence.from_initial_position(
            Point(50, 170, 150),
            Quaternion.from_euler(Point(0, 0, np.pi)),
            Point(-30, 0, 0)
        )
        self.assertEqual(seq.x.iloc[0], 50)
        self.assertEqual(seq.rx.iloc[0], 00)
        self.assertEqual(seq.dx.iloc[0], -30)

    def test_from_line(self):
        initial = Sequence.from_initial_position(
            Point(50, 170, 150),
            Quaternion.from_euler(Point(0, 0, np.pi)),
            Point(-30, 0, 0)
        )

        line = Sequence.from_line(initial, 50, 50)
        pass
