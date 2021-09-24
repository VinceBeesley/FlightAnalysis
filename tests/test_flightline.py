import unittest

from flightdata.data import Flight, Fields
from flightanalysis.flightline import FlightLine, Box
from geometry import GPSPosition, Point, Points, Quaternions
from math import pi, cos, sin
import numpy as np

p21 = Flight.from_csv('./tests/P21.csv')


class TestBox(unittest.TestCase):

    def test_from_initial(self):
        box = Box.from_initial(p21)
        self.assertAlmostEqual(box.pilot_position.latitude, 51.459964, 2)
        self.assertAlmostEqual(box.pilot_position.longitude, -2.791504, 2)

        self.assertAlmostEqual(box.heading, 152.55998 * pi / 180, 3)


class TestFlightLine(unittest.TestCase):

    def test_from_box(self):
        box = Box.from_json('./tests/gordano_box.json')

        fl = FlightLine.from_box(box, GPSPosition(**p21.origin()))

        np.testing.assert_array_almost_equal(
            fl.transform_to.rotate(Point(1.0, 0.0, 0.0)).to_list(),
            Point(-0.514746, -0.857342, 0.0).to_list()
        )   # My box faces south east ish, so world north should be -x and -y in contest frame

        np.testing.assert_array_almost_equal(
            fl.transform_to.translation.to_list(),
            Point(3.922876, -3.664429,  0.).to_list()
        )   # Translation should be small, because I turn on close to the pilot position.


    def test_from_box_true_north(self):
        home = GPSPosition(39, -105)

        # Box heading specified in radians from North (clockwise)
        box = Box('north', home, 0)

        fl = FlightLine.from_box(box, home)

        oneMeterNorth_NED = Point(1, 0, 0)
        oneMeterNorth_ENU = Point(0, 1, 0)

        np.testing.assert_array_almost_equal(
            fl.transform_from.rotate(oneMeterNorth_NED).to_list(),
            oneMeterNorth_ENU.to_list()
        )   # Box faces due North, so NED (1,0,0) should be (0,1,0) in ENU world frame

        np.testing.assert_array_almost_equal(
            fl.transform_to.rotate(oneMeterNorth_ENU).to_list(),
            oneMeterNorth_NED.to_list()
        )   # Box faces due North, so NED (1,0,0) should be (0,1,0) in ENU world frame

        # lat/lon to x/y is problematic over large distances; need to work with x/y displacements
        # relative to home to avoid issues with accuracy
        # 0.001 degree of latitude at 39N is 111.12 meters: http://www.csgnetwork.com/gpsdistcalc.html
        north_of_home = GPSPosition(39.001, -105)
        deltaPos = home.__sub__(north_of_home)
        np.testing.assert_array_almost_equal(
            deltaPos.to_list(),
            [111.12, 0, 0],
            0
        )


    def test_from_box(self):
        box = Box.from_json('./tests/gordano_box.json')

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

    def test_transform_from(self):
        flightline = FlightLine.from_initial_position(p21)

        npoint = flightline.transform_to.point(Point(1, 0, 0))
        self.assertAlmostEqual(npoint.x, flightline.contest.x_axis.x, 4)

    def test_from_covariance(self):
        flightline = FlightLine.from_covariance(p21)
        self.assertAlmostEqual(flightline.contest.y_axis.y,
                               cos((144.8 * pi / 180) - pi / 2), 1)


    def test_flightline_headings(self):
        pilotNorth_ENU = Point(0, 1, 1)
        home = GPSPosition(**p21.origin())
        
        ned = Points.from_pandas(p21.read_fields(Fields.POSITION))
        rned = Quaternions.from_euler(Points.from_pandas(p21.read_fields(Fields.ATTITUDE)))

        #North Facing
        enu_flightline =FlightLine.from_box(Box('test',home,0.0),home)
        enu = enu_flightline.transform_to.point(ned)
        renu = enu_flightline.transform_to.quat(rned)  # TODO think of a test for this
        np.testing.assert_array_almost_equal(ned.x, enu.y)
        np.testing.assert_array_almost_equal(ned.y, enu.x)
        np.testing.assert_array_almost_equal(ned.z, -enu.z)

        pilotNorth_NED = Point(1, 0, -1)
        boxNorth = enu_flightline.transform_to.point(pilotNorth_NED)
        np.testing.assert_array_almost_equal(pilotNorth_ENU.to_tuple(), boxNorth.to_tuple())

        #South Facing
        wsu_flightline =FlightLine.from_box(Box('test',home,np.pi),home)
        wsu = wsu_flightline.transform_to.point(ned)
        rwsu = wsu_flightline.transform_to.quat(rned)  # TODO think of a test for this
        np.testing.assert_array_almost_equal(ned.x, -wsu.y)
        np.testing.assert_array_almost_equal(ned.y, -wsu.x)
        np.testing.assert_array_almost_equal(ned.z, -wsu.z)

        pilotNorth_NED = Point(-1, 0, -1)
        boxNorth = wsu_flightline.transform_to.point(pilotNorth_NED)
        np.testing.assert_array_almost_equal(pilotNorth_ENU.to_tuple(), boxNorth.to_tuple())

        #West Facing
        nwu_flightline =FlightLine.from_box(Box('test',home,-np.pi/2),home)
        nwu = nwu_flightline.transform_to.point(ned)
        rnwu = nwu_flightline.transform_to.quat(rned)  # TODO think of a test for this
        np.testing.assert_array_almost_equal(ned.x, nwu.x)
        np.testing.assert_array_almost_equal(ned.y, -nwu.y)
        np.testing.assert_array_almost_equal(ned.z, -nwu.z)

        pilotNorth_NED = Point(0, -1, -1)
        boxNorth = nwu_flightline.transform_to.point(pilotNorth_NED)
        np.testing.assert_array_almost_equal(pilotNorth_ENU.to_tuple(), boxNorth.to_tuple())



    def test_transform_from_to(self):
        fl = FlightLine.from_covariance(p21)
        ned = Points.from_pandas(p21.read_fields(Fields.POSITION))
        np.testing.assert_array_almost_equal(
            ned.data,
            fl.transform_from.point(fl.transform_to.point(ned)).data
        )
        rned = Quaternions.from_euler(Points.from_pandas(p21.read_fields(Fields.ATTITUDE)))
        np.testing.assert_array_almost_equal(
            rned.data,
            fl.transform_from.quat(fl.transform_to.quat(rned)).data
        )


if __name__ == "__main__":
    unittest.main()
