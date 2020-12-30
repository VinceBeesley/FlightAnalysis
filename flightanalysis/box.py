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


from geometry import GPSPosition, Coord, Point
import numpy as np
import pandas as pd
import math
from Typing import Union


class Box(object):
    '''Class to define an aerobatic box in the world'''

    def __init__(self, name, pilot_position: GPSPosition = None, y_axis_position: GPSPosition = None):
        self._name = name
        self._pilot_position = pilot_position
        self._y_axis_position = y_axis_position

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
        return self._name + '\n' + str(self._pilot_position) + '\n' + str(self._y_axis_position)

    @property
    def pilot_position(self) -> GPSPosition:
        return self._pilot_position

    @property
    def y_axis_position(self) -> GPSPosition:
        return self._y_axis_position


class FlightLine(object):
    '''class to define where the flight line is in relation to the raw input data'''

    def __init__(self, startup_box: Box, desired_box: Box):

        self._base_coord = Coord(
            origin=Point(),
            y_axis=startup_box.y_axis_position - startup_box.pilot_position,
            z_axis=Point(0, 0, 100)
        )

        self._box_coord = Coord(
            origin=desired_box.pilot_position - startup_box.pilot_position,
            y_axis=desired_box.y_axis_position - startup_box.pilot_position,
            z_axis=Point(0, 0, 100),
        )

    @property
    def box_coord(self) -> Coord:
        return self._box_coord

    def point_to_box(self, location: Union(Point, Quaternion)):
        # TODO add the translation
        return location.rotate(self.box_coord.rotation_matrix)

    def _field_point_to_box(self, x, y, z):
        box_point = self.point_to_box(Point(x, y, z))
        return box_point.x, box_point.y, box_point.z

    @property
    def field_point_to_box(self):
        return np.vectorize(self._field_point_to_box)

    def _field_quat_to_box(self, w, x, y, z):
        box_point = self.point_to_box(Quaternion(w, Point(x, y, z)))
        return box_point.w, box_point.x, box_point.y, box_point.z

    @property
    def field_quat_to_box(self):
        return np.vectorize(self._field_quat_to_box)
