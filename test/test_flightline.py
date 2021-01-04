import unittest
from flightanalysis.flightline import FlightLine, Box
from geometry import GPSPosition
import math



class TestBox(unittest.TestCase):
    def test_directions(self):
        
        north_facing_box = Box(
            'test',
            GPSPosition(51.464382, -2.940711),
            GPSPosition(51.491542, -2.941218)
        )
        self.assertAlmostEqual(north_facing_box.x_direction.y, 1, 3)
        self.assertAlmostEqual(north_facing_box.x_direction.x, 0, 1)
        self.assertEqual(north_facing_box.x_direction.z, 0)

        self.assertAlmostEqual(north_facing_box.y_direction.y, 0, 1)
        self.assertAlmostEqual(north_facing_box.y_direction.x, -1, 2)
        self.assertEqual(north_facing_box.y_direction.z, 0)



class TestFlightLine(unittest.TestCase):
    def test_setup(self):
        home = GPSPosition(51.459387, -2.791393)

        new = GPSPosition(51.458876, -2.789092)
        coord = new.to_seu(home)
        self.assertAlmostEqual(
            math.sqrt(coord[0] ** 2 + coord[1] ** 2), 165.6835176, 5)
