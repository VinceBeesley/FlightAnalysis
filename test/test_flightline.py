import unittest

from flightdata.data import Flight
from flightanalysis.flightline import FlightLine, Box
from geometry import GPSPosition, Point
from math import pi, cos, sin


p21 = Flight.from_csv('./test/P21.csv')


class TestBox(unittest.TestCase):
    def test_directions(self):

        north_facing_box = Box(
            'test',
            GPSPosition(51.464382, -2.940711),
            
        )
        self.assertAlmostEqual(north_facing_box.x_direction.y, 1, 3)
        self.assertAlmostEqual(north_facing_box.x_direction.x, 0, 1)
        self.assertEqual(north_facing_box.x_direction.z, 0)

        self.assertAlmostEqual(north_facing_box.y_direction.y, 0, 1)
        self.assertAlmostEqual(north_facing_box.y_direction.x, 1, 2)
        self.assertEqual(north_facing_box.y_direction.z, 0)

    def test_initial(self):
        box = Box.from_initial(p21)
        self.assertAlmostEqual(box.pilot_position.latitude, 51.459964, 2)
        self.assertAlmostEqual(box.pilot_position.longitude, -2.791504, 2)

        self.assertAlmostEqual(box.heading, 152.55998 * pi / 180, 3)

        self.assertAlmostEqual(box.y_direction.y, cos(box.heading - pi / 2), 3)
        self.assertAlmostEqual(abs(box.y_direction.x),
                               sin(box.heading - pi / 2), 3)

        self.assertAlmostEqual(box.x_direction.y, -
                               sin(box.heading - pi / 2), 3)
        self.assertAlmostEqual(box.x_direction.x, -
                               cos(box.heading - pi / 2), 3)


class TestFlightLine(unittest.TestCase):

    def test_initial(self):
        flightline = FlightLine.from_initial_position(p21)
        self.assertAlmostEqual(flightline.world.origin.x, 0, 2)
        self.assertAlmostEqual(flightline.world.origin.y, 0, 2)

        self.assertAlmostEqual(flightline.contest.y_axis.y, cos(
            (152.55998 * pi / 180) - pi / 2), 2)

    def test_transform_to(self):
        flightline = FlightLine.from_initial_position(p21)

        npoint = flightline.transform_to.point(Point(1, 0, 0))
        self.assertAlmostEqual(npoint.x, flightline.contest.x_axis.x, 4)

    def test_from_covariance(self):
        flightline = FlightLine.from_covariance(p21)
        self.assertAlmostEqual(flightline.contest.y_axis.y,
                               cos((144.8 * pi / 180) - pi / 2), 1)
