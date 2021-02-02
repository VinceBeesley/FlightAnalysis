from flightanalysis.section import Section
from flightanalysis.state import State
from flightanalysis.flightline import Box, FlightLine
import unittest
from geometry import Point, Quaternion, Points, Quaternions
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
        self.assertIsInstance(state.pos, Point)

    def test_from_line(self):
        """from inverted at 30 m/s, fly in a stright line for 1 second
        """
        initial = State(
            Point(60, 170, 150),
            Quaternion.from_euler(Point(np.pi, 0, np.pi)),
            Point(30, 0, 0)
        )  # somthing like the starting pos for a P21 from the right

        line = Section.from_line(
            initial,
            np.linspace(0, 1, 5)
        )
        np.testing.assert_array_almost_equal(
            line.pos.iloc[-1], [30, 170, 150]
        )
        np.testing.assert_array_almost_equal(
            line.bvel, np.tile(np.array([30, 0, 0]), (5, 1))
        )
        np.testing.assert_array_almost_equal(
            line.att, np.tile(
                list(Quaternion.from_euler(Point(np.pi, 0, np.pi))),
                (5, 1))
        )

    def test_from_roll(self):
        """From inverted at 30 m/s perform 1/2 a roll at 180 degrees / second
        """
        initial = State(
            Point(30, 170, 150),
            Quaternion.from_euler(Point(np.pi, 0, np.pi)),
            Point(30, 0, 0),
            Point(np.pi, 0, 0)
        )

        line = Section.from_line(initial, np.linspace(0, 1, 5))

        np.testing.assert_array_almost_equal(
            line.pos.iloc[-1], [0, 170, 150]
        )
        np.testing.assert_array_almost_equal(
            line.bvel, np.tile(np.array([30, 0, 0]), (5, 1))
        )
        np.testing.assert_array_almost_equal(
            list(Point(0, 0, 1)),
            Quaternions(line.att.to_numpy()).transform_point(
                Point(0, 0, 1)).data[-1]
        )

    def test_from_radius(self):
        """do the outside loop at the start of the P sequence"""
        initial = State(
            Point(0, 170, 150),
            Quaternion.from_euler(Point(np.pi, 0, np.pi)),
            Point(10 * np.pi, 0, 0),  # 620 m in 10 seconds
            Point(0, np.pi / 5, 0)
        )

        radius = Section.from_radius(initial, np.linspace(0, 10, 10))
        np.testing.assert_array_almost_equal(
            list(radius.get_state_from_index(-1).pos),
            list(Point(0, 170, 150))
        )

    def test_body_to_world(self):

        seq = Section.from_flight(
            flight, FlightLine.from_initial_position(flight))

        pnew = seq.body_to_world(Point(1, 0, 0))

        self.assertIsInstance(pnew, Points)

    def test_subset(self):
        seq = Section.from_flight(
            flight, FlightLine.from_initial_position(flight))

        self.assertIsInstance(seq.subset(100, 200), Section)
        self.assertAlmostEqual(seq.subset(100, 200).data.index[-1], 200, 2)

        self.assertAlmostEqual(seq.subset(-1, 200).data.index[-1], 200, 2)

        self.assertAlmostEqual(
            seq.subset(-1, -1).data.index[-1],
            seq.data.index[-1],
            2
        )

    def test_get_state(self):
        seq = Section.from_flight(
            flight, FlightLine.from_initial_position(flight))
        st = seq.get_state_from_time(100)
        self.assertIsInstance(st, State)

    def test_stack(self):
        initial = State(
            Point(10 * np.pi, 170, 150),
            Quaternion.from_euler(Point(np.pi, 0, np.pi)),
            Point(10 * np.pi, 0, 0),
            Point(np.pi, 0, 0)
        )

        line = Section.from_line(initial, np.linspace(0, 1, 5))

        last_state = line.get_state_from_index(-1)
        last_state.brvel = Point(0, np.pi / 5, 0)

        radius = Section.from_radius(last_state, np.linspace(0, 10, 10))

        combo = Section.stack([line, radius])

        self.assertEqual(len(combo.data), 14)
        self.assertEqual(combo.data.index[-1], 11)

        self.assertIsInstance(combo.get_state_from_time(10), State)
