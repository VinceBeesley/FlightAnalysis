import unittest

from flightdata.data import Flight
from flightanalysis.flightline import FlightLine, Box
from geometry import GPSPosition
from math import pi, cos, sin




class TestBox(unittest.TestCase):
    def test_directions(self):

        north_facing_box = Box(
            'test',
            GPSPosition(51.464382, -2.940711),
            0
        )
        self.assertAlmostEqual(north_facing_box.x_direction.y, 1, 3)
        self.assertAlmostEqual(north_facing_box.x_direction.x, 0, 1)
        self.assertEqual(north_facing_box.x_direction.z, 0)

        self.assertAlmostEqual(north_facing_box.y_direction.y, 0, 1)
        self.assertAlmostEqual(north_facing_box.y_direction.x, 1, 2)
        self.assertEqual(north_facing_box.y_direction.z, 0)

    def test_initial(self):
        p21 = Flight.from_log('./test/p21.BIN')

        box = Box.from_initial(p21)
        self.assertAlmostEqual(box.pilot_position.latitude, 51.459964, 3)
        self.assertAlmostEqual(box.pilot_position.longitude, -2.791504, 3)
        
        self.assertAlmostEqual(box.heading, 153.36 * pi / 180, 2)
        
        self.assertAlmostEqual(box.y_direction.y, cos(box.heading - pi / 2), 2)
        self.assertAlmostEqual(abs(box.y_direction.x), sin(box.heading - pi / 2), 2)

        self.assertAlmostEqual(box.x_direction.y, -sin(box.heading - pi /2 ), 2)
        self.assertAlmostEqual(box.x_direction.x, -cos(box.heading - pi /2 ), 2)


class TestFlightLine(unittest.TestCase):

    def test_initial(self):
        pass

