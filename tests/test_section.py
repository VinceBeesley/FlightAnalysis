from flightanalysis.section import Section
from flightanalysis.state import State
from flightanalysis.flightline import Box, FlightLine
from flightanalysis.schedule import Schedule
from flightanalysis.schedule import p21
import unittest
from geometry import Point, Quaternion, Points, Quaternions, GPSPosition
from flightdata import Flight, Fields
import numpy as np
import pandas as pd
from io import open
from json import load
import os

flight = Flight.from_csv('tests/P21_new.csv')

box = Box.from_json('./tests/gordano_box.json')

class TestSection(unittest.TestCase):
    def test_from_flight(self):
        seq = Section.from_flight(flight, box)
        self.assertIsInstance(seq.x, pd.Series)
        self.assertIsInstance(seq.y, pd.Series)
        self.assertIsInstance(seq.z, pd.Series)
        self.assertIsInstance(seq.rw, pd.Series)
        self.assertIsInstance(seq.rx, pd.Series)
        self.assertIsInstance(seq.ry, pd.Series)
        self.assertIsInstance(seq.rz, pd.Series)
        self.assertGreater(seq.z.mean(), 0)
        np.testing.assert_array_less(np.abs(seq.pos.to_numpy()[0]), 50.0 )
    
    def test_to_csv(self):
        seq = Section.from_flight(flight, box)
        csv_file = seq.to_csv('tests/test.csv')
        seq2 = Section.from_csv(csv_file) 
        self.assertEqual(seq.duration, seq2.duration)
        os.remove(csv_file)

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
            initial.transform,
            10,
            100
        )
        np.testing.assert_array_almost_equal(
            line.pos.iloc[-1], [-40, 170, 150]
        )
        np.testing.assert_array_almost_equal(
            line.bvel, np.tile(np.array([10, 0, 0]), (len(line.data.index), 1))
        )
        np.testing.assert_array_almost_equal(
            line.att, np.tile(
                list(Quaternion.from_euler(Point(np.pi, 0, np.pi))),
                (len(line.data.index), 1))
        )


    def test_from_loop(self):
        """do the outside loop at the start of the P sequence"""
        initial = State(
            Point(0, 170, 150),
            Quaternion.from_euler(Point(np.pi, 0, np.pi)),
            Point(10 * np.pi, 0, 0),  # 620 m in 10 seconds
            Point(0, np.pi / 5, 0)
        )

        radius = Section.from_loop(initial.transform, 10*np.pi, 1, 50)
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
        self.assertAlmostEqual(seq.subset(100, 200).data.index[-1], 200, 0)

        self.assertAlmostEqual(seq.subset(-1, 200).data.index[-1], 200, 0)

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

        line = Section.from_line(initial.transform, 30, 20)

        last_state = line.get_state_from_index(-1)
        
        radius = Section.from_loop(last_state.transform, 30, 1, 50)

        combo = Section.stack([line, radius])

        self.assertEqual(len(combo.data), len(line.data) + len(radius.data) - 1)
        self.assertEqual(combo.data.iloc[-1].bvx, 30)

        self.assertIsInstance(combo.get_state_from_time(10), State)

        self.assertEqual(
            radius.data.index[-1] + line.data.index[-1],
            combo.data.index[-1]
        ) 

        self.assertEqual(combo.get_state_from_time(0.0).pos, combo.get_state_from_index(0).pos)

        self.assertEqual(combo.data.index.name, "time_index")

    def test_align(self):
        flight = Flight.from_csv("tests/nice_p.csv")

        flown = Section.from_flight(flight, FlightLine.from_box(box, GPSPosition(**flight.origin()))).subset(100, 493)

        template = p21.scale_distance(170.0).create_raw_template("left", 30, 170)
        
        aligned = Section.align(flown, template)

        self.assertEqual(len(aligned[1].data), len(flown.data))
        np.testing.assert_array_less(np.abs(aligned[1].pos.to_numpy()[0]), 200.0 )


if __name__ == '__main__':
    unittest.main()