import unittest

from flightdata.data import Flight, Fields
from flightanalysis.flightline import FlightLine, Box
from geometry import GPSPosition, Point, Points, Quaternions
from math import pi, cos, sin
import numpy as np
import pytest


@pytest.fixture(scope="session")
def flight():
    return Flight.from_csv('tests/test_inputs/test_log_00000052_flight.csv')


@pytest.fixture(scope="session")
def  box():
    return Box.from_json('tests/test_inputs/test_log_box.json')


def test_from_initial(flight):
    box = Box.from_initial(flight)
    assert pytest.approx(box.pilot_position.latitude, 51.6418436, 2)
    
    assert pytest.approx(box.pilot_position.longitude, -2.5260131, 2)

    assert pytest.approx(box.heading, np.radians(139.8874730), 3)


def test_to_dict(flight):
    box = Box.from_initial(flight)
    di = box.to_dict()
    assert di["name"] ==  "origin"
    assert di["pilot_position"]['latitude'] == 51.6418417


def test_from_box(flight, box):
    fl = FlightLine.from_box(box, flight.origin)

    np.testing.assert_array_almost_equal(
        np.sign(fl.transform_to.rotate(Point(1.0, 0.0, 0.0)).to_list()),
        [-1,-1,0]
    )   # My box faces south east ish, so world north should be -x and +y in contest frame

    assert abs(fl.transform_to.rotate(Point(1.0, 0.0, 0.0))) < 3   # Translation should be small, because I turn on close to the pilot position.


@unittest.skip
def test_from_box_true_north():
    home = GPSPosition(39, -105)

    # Box heading specified in radians from North (clockwise)
    box = Box('north', home, 0)

    fl = FlightLine.from_box(box, home)

    oneMeterNorth_NED = Point(1, 0, 0)
    
    np.testing.assert_array_almost_equal(
        fl.transform_from.rotate(oneMeterNorth_NED).to_list(),
        oneMeterNorth_NED.to_list()
    )  

    np.testing.assert_array_almost_equal(
        fl.transform_to.rotate(oneMeterNorth_NED).to_list(),
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


def test_initial(flight):
    flightline = FlightLine.from_initial_position(flight)
    pytest.approx(flightline.world.origin.x, 0, 2)
    pytest.approx(flightline.world.origin.y, 0, 2)

    pytest.approx(
        flightline.contest.y_axis.y, 
        cos((152.55998 * pi / 180) - pi / 2), 
        2
    )



def test_transform_to(flight):
    flightline = FlightLine.from_initial_position(flight)

    npoint = flightline.transform_to.point(Point(1, 0, 0))
    pytest.approx(npoint.x, flightline.contest.x_axis.x, 4)

def test_transform_from(flight):
    flightline = FlightLine.from_initial_position(flight)

    npoint = flightline.transform_to.point(Point(1, 0, 0))
    pytest.approx(npoint.x, flightline.contest.x_axis.x, 4)

def test_from_covariance(flight):
    flightline = FlightLine.from_covariance(flight)
    pytest.approx(flightline.contest.y_axis.y,
                            cos((144.8 * pi / 180) - pi / 2), 1)


def test_flightline_headings(flight):
    pilotNorth_ENU = Point(0, 1, 1)
    home = flight.origin
    
    ned = Points.from_pandas(flight.read_fields(Fields.POSITION))
    rned = Quaternions.from_euler(Points.from_pandas(flight.read_fields(Fields.ATTITUDE)))

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



def test_transform_from_to(flight):
    fl = FlightLine.from_covariance(flight)
    ned = Points.from_pandas(flight.read_fields(Fields.POSITION))
    np.testing.assert_array_almost_equal(
        ned.data,
        fl.transform_from.point(fl.transform_to.point(ned)).data
    )
    rned = Quaternions.from_euler(Points.from_pandas(flight.read_fields(Fields.ATTITUDE)))
    np.testing.assert_array_almost_equal(
        rned.data,
        fl.transform_from.quat(fl.transform_to.quat(rned)).data
    )


def test_to_f3azone(box):
    zone_string = box.to_f3a_zone()
    lines = zone_string.split("\n")
    
    assert lines[0] == "Emailed box data for F3A Zone Pro - please DON'T modify!"
    assert lines[1] == box.name

    pilot = GPSPosition(float(lines[2]), float(lines[3]))

    centre = GPSPosition(float(lines[4]), float(lines[5]))

    box_copy = Box.from_points("tem", pilot, centre)

    assert pytest.approx(box_copy.heading, box.heading)
    assert float(lines[6]) == 120



if __name__ == "__main__":
    unittest.main()
