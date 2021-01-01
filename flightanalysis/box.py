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

from geometry import GPSPosition, Coord, Point, Quaternion
from geometry.coordinate_frame import Transformation
from geometry.point import cross_product
import numpy as np
import pandas as pd
import math
from typing import Union


class Box(object):
    '''Class to define an aerobatic box in the world'''

    def __init__(self, name, pilot_position: GPSPosition, y_axis_position: GPSPosition):
        self.name = name
        self.pilot_position = pilot_position
        self.y_axis_position = y_axis_position
        self._y_direction = None
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
        return self.name + '\n' + str(self.pilot_position) + '\n' + str(self.y_axis_position)

    @property
    def y_direction(self) -> Point:
        if not self._y_direction:
            self._y_direction = (self.y_axis_position -
                                 self.pilot_position).unit()
        return self._y_direction

    @property
    def x_direction(self) -> Point:
        if not self._x_direction:
            self._x_direction = cross_product(
                self.z_direction, self.y_direction)
        return self._x_direction


class FlightLine(object):
    '''class to define where the flight line is in relation to the raw input data'''

    def __init__(self, world: Coord, contest: Coord):
        self.world = world
        self.contest = contest
        self.transform = Transformation(self.contest, self.world)

    @staticmethod
    def from_boxes(startup_box: Box, desired_box: Box):
        return FlightLine(
            Coord(
                Point(0, 0, 0),
                startup_box.x_direction,
                startup_box.y_direction,
                startup_box.z_direction
            ),
            Coord(
                desired_box.origin - startup_box.origin,
                desired_box.x_direction,
                desired_box.y_direction,
                desired_box.z_direction
            )
        )
