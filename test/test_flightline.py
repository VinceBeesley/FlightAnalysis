import unittest
from flightanalysis.flightline import FlightLine, Box
from geometry import GPSPosition
import math


class TestFlightLine(unittest.TestCase):
    def test_setup(self):
        home = GPSPosition(51.459387, -2.791393)

        new = GPSPosition(51.458876, -2.789092)
        coord = new.to_seu(home)
        self.assertAlmostEqual(
            math.sqrt(coord[0] ** 2 + coord[1] ** 2), 165.6835176, 5)
