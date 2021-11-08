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
from math import atan2, pi
from json import load, dump


class Box(object):
    '''This class defines an aerobatic box in the world, it uses the pilot position and the direction 
    in which the pilot is facing (normal to the main aerobatic manoeuvering plane)'''

    def __init__(self, name, pilot_position: GPSPosition, heading: float, club:str=None, country:str=None):
        self.name = name
        self.club=club
        self.country=country
        self.pilot_position = pilot_position
        self.heading = heading

    @staticmethod
    def from_f3a_zone_file(file_path: str):
        with open(file_path, "r") as f:
            lines = f.read().splitlines()
        return Box.from_points(
            lines[1],
            GPSPosition(float(lines[2]), float(lines[3])),
            GPSPosition(float(lines[4]), float(lines[5]))
        )

    def to_dict(self) -> dict:
        temp = self.__dict__.copy()
        temp["pilot_position"] = self.pilot_position.to_dict()
        return temp

    @staticmethod
    def from_json(file):
        if hasattr(file, 'read'):
            data = load(file)
        else:
            with open(file, 'r') as f:
                data = load(f)
        read_box = Box(
            data['name'], 
            GPSPosition(**data['pilot_position']), 
            data['heading'],
            data['club'],
            data['country'])
        return read_box

    def to_json(self, file):
        with open(file, 'w') as f:
            dump(self.to_dict(), f)

    def __str__(self):
        return "Box:{}".format(self.to_dict())

    @staticmethod
    def from_initial(flight: Flight):
        '''Generate a box based on the initial position and heading of the model at the start of the log. 
        This is a convenient, but not very accurate way to setup the box. 
        '''
        first = flight.data.iloc[0]
        home = GPSPosition(*flight.read_fields(Fields.GLOBALPOSITION).iloc[0])
            
        heading = Quaternion(*first[Fields.QUATERNION.names]).transform_point(Point(1, 0, 0))

        return Box('origin', home, atan2(heading.y, heading.x), "unknown", "unknown")

    @staticmethod
    def from_covariance(flight: Flight):
        """Generate a box by effectively fitting a best fit line through a whole flight. 
        Again, this is a convenient method but not very reliable as it relies on the pilot to have
        flown on the correct manoeuvering plane for most of the flight. 
        TODO it sometimes points in the wrong direction too.
        """
        pos = flight.read_fields(Fields.POSITION).iloc[:, :2]
        # generate the covariance matrix
        ca = np.cov(pos, y=None, rowvar=0, bias=1)
        v, vect = np.linalg.eig(ca)  # calculate the eigenvectors
        rotmat = np.identity(3)  # convert to a 3x3
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

    @staticmethod
    def from_points(name, pilot: GPSPosition, centre: GPSPosition):
        direction = centre - pilot
        return Box(
            name,
            pilot,
            atan2(direction.x, direction.y) + pi/2)


class FlightLine(object):
    '''class to define where the flight line is in relation to the raw input data
    It contains two coordinate frames (generally used for reference / debugging only) and two transformations, 
    which will take geometry to and from these reference frames.  

    '''

    def __init__(self, world: Coord, contest: Coord):
        """Default FlightLine constructor, takes the world and contest coordinate frames

        Args:
            world (Coord): The world coordinate frame, for Ardupilot this is NED.
            contest (Coord): The desired coordinate frame. Generally in PyFlightCoach (and in this classes constructors)
                            this should be origin on the pilot position, x axis out the pilots right shoulder, y axis is the
                            direction the pilot is facing, Z axis up. (This assumes the pilot is standing on the pilot position, 
                            facing the centre marker)

        """
        self.world = world
        self.contest = contest
        self.transform_to = Transformation.from_coords(contest, world)
        self.transform_from = Transformation(-self.transform_to.translation,
                                             self.transform_to.rotation.conjugate())

    @staticmethod
    def from_box(box: Box, world_home: GPSPosition):
        """Constructor from a Box instance. This method assumes the input data is in the 
        Ardupilot default World frame (NED). It creates the contest frame from the box as described in __init__, 
        ie z up, y in the box heading direction. 

        Args:
            box (Box): box defining the contest coord
            world_home (GPSPosition): home position of the input data

        Returns:
            FlightLine
        """
        return FlightLine(


            # this just sets x,y,z origin to zero and unit vectors = [1 0 0] [0 1 0] [0 0 1]
            Coord.from_zx(Point(0, 0, 0), Point(0, 0, 1), Point(1, 0, 0)),
            Coord.from_yz(
                box.pilot_position - world_home,
                Point(cos(box.heading), sin(box.heading), 0),
                Point(0.0, 0.0, -1.0)
            )
        )

    @staticmethod
    def from_initial_position(flight: Flight):
        return FlightLine.from_box(Box.from_initial(flight), flight.origin)

    @staticmethod
    def from_heading(flight: Flight, heading: float):
        """generate a flightline based on the turn on gps position and a heading

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
        return FlightLine.from_box(Box.from_covariance(flight), flight.origin)
