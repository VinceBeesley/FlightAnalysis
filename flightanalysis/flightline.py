"""
This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.
This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with
this program. If not, see <http://www.gnu.org/licenses/>.
"""

from geometry import GPSPosition, Coord, Point, Quaternion, Transformation, cross_product
from typing import Union
from flightdata import Flight, Fields
from math import atan2, sin, cos
import numpy as np


class Box(object):
    '''Class to define an aerobatic box in the world'''

    def __init__(self, name, pilot_position: GPSPosition, heading: float):
        self.name = name
        self.pilot_position = pilot_position
        self.heading = heading
        self.y_direction = Point(cos(self.heading), sin(self.heading), 0)
        self._x_direction = None
        self.z_direction = Point(0, 0, 1)

    @staticmethod
    def from_f3a_zone_file(file_path: str):
        with open(file_path, "r") as f:
            lines = f.read().splitlines()
        return Box(
            lines[1],
            GPSPosition(float(lines[2]), float(lines[3])),
            GPSPosition(float(lines[4]), float(lines[5]))
        )

    def __str__(self):
        return self.name + '\n' + str(self.pilot_position) + '\n' + str(self.heading)

    @property
    def x_direction(self) -> Point:
        if not self._x_direction:
            self._x_direction = cross_product(
                self.y_direction, self.z_direction)
        return self._x_direction

    @staticmethod
    def from_initial(flight: Flight):
        '''Generate a box representing the default flight coordinate frame'''
        first = flight.data.iloc[0]
        home = GPSPosition(
            first.global_position_latitude,
            first.global_position_longitude
        )

        heading = Point(1, 0, 0).rotate(
            Point(first.attitude_roll, first.attitude_pitch,
                  first.attitude_yaw).to_rotation_matrix()
        )

        return Box('origin', home, atan2(heading.y, heading.x))

    @staticmethod
    def from_covariance(flight: Flight):
        pos = flight.read_fields(Fields.POSITION).iloc[:, :2]
        ca = np.cov(pos, y=None, rowvar=0, bias=1) # generate the covariance matrix
        v, vect = np.linalg.eig(ca)  # calculate the eigenvectors
        rotmat = np.identity(3) # convert to a 3x3
        rotmat[:-1, :-1] = np.linalg.inv(np.transpose(vect))
        heading = Point(1, 0, 0).rotate(rotmat)
        first = flight.data.iloc[0]
        return Box(
            'covariance',
            GPSPosition(
                first.global_position_latitude,
                first.global_position_longitude
            ),
            atan2(heading.y, heading.x)
        )


class FlightLine(object):
    '''class to define where the flight line is in relation to the raw input data'''

    def __init__(self, world: Coord, contest: Coord):
        self.world = world
        self.contest = contest
        self.transform_to = Transformation.from_coords(self.contest, self.world)
        self.transform_from = Transformation.from_coords(self.world, self.contest)

    @staticmethod
    def from_box(box):
        return FlightLine(
            Coord.from_zx(Point(0, 0, 0), Point(0, 0, 1), Point(1, 0, 0)),
            Coord(
                Point(0, 0, 0),
                -box.x_direction,
                box.y_direction,
                -box.z_direction
            )
        )

    @staticmethod
    def from_initial_position(flight: Flight):
        return FlightLine.from_box(Box.from_initial(flight))

    @staticmethod
    def from_heading(flight: Flight, heading: float):
        """generate a flightlint based on the turn on gps position and a heading

        Args:
            flight (Flight): the flight to take the initial gps position from.
            heading (float): the direction towards centre in radians
        """

        return FlightLine.from_box(
            Box(
                'heading',
                GPSPosition(
                    flight.data.iloc[0].global_position_latitude,
                    flight.data.iloc[0].global_position_longitude
                ),
                heading
            ))

    @staticmethod
    def from_covariance(flight: Flight):
        """generate a flightline from a flight based on the covariance matrix

        Args:
            flight (Flight): 
        """
        return FlightLine.from_box(Box.from_covariance(flight))
