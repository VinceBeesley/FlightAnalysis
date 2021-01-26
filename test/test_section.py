from flightanalysis.section import Section
from flightanalysis.state import State
from flightanalysis.flightline import Box, FlightLine
import unittest
from geometry import Point, Quaternion
from flightdata import Flight, Fields
import numpy as np
import pandas as pd


flight = Flight.from_csv('test/P21.csv')


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

    def test_generate_state(self):
        seq = Section.from_flight(
            flight, FlightLine.from_initial_position(flight))
        state = seq.get_state_from_index(20)
        self.assertIsInstance(state.x, float)
        self.assertIsInstance(state.pos, tuple)

    def test_from_line(self):
        initial = State.from_posattvel(
            Point(60, 170, 150),
            Quaternion.from_euler(Point(np.pi, 0, np.pi)),
            Point(-30, 0, 0)
        )  # somthing like the starting pos for a P21 from the right

        line = Section.from_line(initial, 30, 5)
        self.assertEqual(line.x[-1], 30)
        self.assertEqual(line.y[-1], 170)
        self.assertEqual(line.dx[-1], -30)

    def test_from_roll(self):
        initial = State.from_posattvel(
            Point(30, 170, 150),
            Quaternion.from_euler(Point(np.pi, 0, np.pi)),
            Point(-30, 0, 0)
        )

        line = Section.from_roll(initial, 30, np.pi, 5)

        self.assertEqual(line.x[-1], 00)
        self.assertEqual(line.y[-1], 170)
        self.assertEqual(line.dx[-1], -30)

        def get_up_vec(index):
            return Quaternion(
                *line.get_state_from_index(index).att
            ).transform_point(Point(0, 0, 1))

        initial_up_vec = get_up_vec(0)
        self.assertAlmostEqual(initial_up_vec.x, 0)
        self.assertAlmostEqual(initial_up_vec.y, 0)
        self.assertAlmostEqual(initial_up_vec.z, -1)

        end_up_vec = get_up_vec(-1)
        self.assertAlmostEqual(end_up_vec.x, 0)
        self.assertAlmostEqual(end_up_vec.y, 0)
        self.assertAlmostEqual(end_up_vec.z, 1)

    def test_from_radius(self):
        initial = State.from_posattvel(
            Point(0, 170, 150),
            Quaternion.from_euler(Point(0, 0, np.pi)),
            Point(-30, 0, 0)
        )

    def test_body_to_world(self):
        seq = Section.from_flight(
            flight, FlightLine.from_initial_position(flight))

        pnew = seq.body_to_world(Point(1,0,0))

        self.assertIsInstance(pnew, Point)
        