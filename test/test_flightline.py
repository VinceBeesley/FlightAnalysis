import unittest

from flightdata.data import Flight
from flightanalysis.flightline import FlightLine, Box
from geometry import GPSPosition, Point
from math import pi, cos, sin
import numpy as np

p21 = Flight.from_csv('./test/P21.csv')


class TestBox(unittest.TestCase):

    def test_from_initial(self):
        box = Box.from_initial(p21)
        self.assertAlmostEqual(box.pilot_position.latitude, 51.459964, 2)
        self.assertAlmostEqual(box.pilot_position.longitude, -2.791504, 2)

        self.assertAlmostEqual(box.heading, 152.55998 * pi / 180, 3)


class TestFlightLine(unittest.TestCase):

    def test_from_box(self):
        box = Box.from_json('./test/gordano_box.json')

        fl = FlightLine.from_box(box, GPSPosition(**p21.origin()))

        np.testing.assert_array_almost_equal(
            fl.transform_to.rotate(Point(1.0, 0.0, 0.0)).to_list(),
            Point(-0.514746, -0.857342, 0.0).to_list()
        )   # My box faces south east ish, so world north should be -x and -y in contest frame

        np.testing.assert_array_almost_equal(
            fl.transform_to.translation.to_list(),
            Point(3.922876, -3.664429,  0.).to_list()
        )   # Translation should be small, because I turn on close to the pilot position.



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
