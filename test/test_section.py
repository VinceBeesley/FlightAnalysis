from flightanalysis.section import Section, State
from flightanalysis.flightline import Box, FlightLine
import unittest
from geometry import Point, Quaternion
from flightdata import Flight, Fields
import numpy as np
import pandas as pd


flight = Flight.from_csv('test/P21.csv')


class TestState(unittest.TestCase):
    def from_posattvel(self):
        seq = State.from_posattvel(
            Point(50, 170, 150),
            Quaternion.from_euler(Point(0, 0, np.pi)),
            Point(-30, 0, 0)
        )
        self.assertEqual(seq.x, 50)
        self.assertEqual(seq.rx, 0)
        self.assertEqual(seq.dx, -30)


class TestSection(unittest.TestCase):
    def test_from_flight(self):
        seq = Section.from_flight(
            flight, FlightLine.from_initial_position(flight))
        self.assertIsInstance(seq.x, pd.Series)
        self.assertIsInstance(seq.y, pd.Series)
        self.assertIsInstance(seq.z, pd.Series)
        self.assertIsInstance(seq.rw, pd.Series)
        self.assertIsInstance(seq.rx, pd.Series)
        self.assertIsInstance(seq.ry, pd.Series)
        self.assertIsInstance(seq.rz, pd.Series)
        self.assertGreater(seq.z.mean(), 0)

    def test_from_line(self):
        initial = State.from_posattvel(
            Point(50, 170, 150),
            Quaternion.from_euler(Point(0, 0, np.pi)),
            Point(-30, 0, 0)
        )

        line = Section.from_line(initial, 50, 50)
        pass
