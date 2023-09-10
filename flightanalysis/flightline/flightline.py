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

from geometry import GPS, Coord, Point, Transformation, Quaternion, PX, PY, PZ, P0, Euler
from typing import Union
import numpy as np
from json import load, dump



class Box(object):
    '''This class defines an aerobatic box in the world, it uses the pilot position and the direction 
    in which the pilot is facing (normal to the main aerobatic manoeuvering plane)'''

    def __init__(self, name, pilot_position: GPS, heading: float, club:str=None, country:str=None):
        self.name = name
        self.club=club
        self.country=country
        self.pilot_position = pilot_position
        self.heading = heading
        self.rotation = Euler(0, 0, -self.heading)

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
            GPS(**data['pilot_position']), 
            data['heading'],
            data['club'],
            data['country'])
        return read_box

    def to_json(self, file):
        with open(file, 'w') as f:
            dump(self.to_dict(), f)

    def __str__(self):
        return "Box:{}".format(self.to_dict())

    def __repr__(self):
        return f'Box(heading={np.degrees(self.heading)},pos={self.pilot_position})'

    @staticmethod
    def from_initial(flight):
        from flightdata import Fields
        '''Generate a box based on the initial position and heading of the model at the start of the log. 
        This is a convenient, but not very accurate way to setup the box. 
        '''
        imu_ready_data = flight.data.loc[flight.imu_ready_time()]

        position = GPS(*imu_ready_data[Fields.GLOBALPOSITION.names])
        heading = Euler(
            *imu_ready_data[Fields.ATTITUDE.names]
        ).transform_point(PX())

        return Box('origin', position[0], np.arctan2(heading.y, heading.x)[0], "unknown", "unknown")

    @staticmethod
    def from_points(name, pilot: GPS, centre: GPS):
        direction = centre - pilot
        return Box(
            name,
            pilot,
            np.arctan2(direction.y[0], direction.x[0])
        )

    def to_f3a_zone(self):
        
        centre = self.pilot_position.offset(
            100 * Point(np.cos(self.heading), np.sin(self.heading), 0.0)
        )

        oformat = lambda val: "{}".format(val)

        return "\n".join([
            "Emailed box data for F3A Zone Pro - please DON'T modify!",
            self.name,
            oformat(self.pilot_position.lat[0]),
            oformat(self.pilot_position.long[0]),
            oformat(centre.lat[0]),
            oformat(centre.long[0]),
            "120"
        ])


    @staticmethod
    def from_f3a_zone(file_path: str):
        if hasattr(file_path, "read"):
            lines = file_path.read().splitlines()
        else:
            with open(file_path, "r") as f:
                lines = f.read().splitlines()
        return Box.from_points(
            lines[1],
            GPS(float(lines[2]), float(lines[3])),
            GPS(float(lines[4]), float(lines[5]))
        )

    @staticmethod
    def from_fcjson_parmameters(data: dict):
        return Box.from_points(
            "FCJ_box",
            GPS(float(data['pilotLat']), float(data['pilotLng'])),
            GPS(float(data['centerLat']), float(data['centerLng']))
        )


    def gps_to_point(self, gps: GPS) -> Point:
        pned = gps - self.pilot_position
        return self.rotation.transform_point(Point(pned.y, pned.x, -pned.z ))


#    def point_to_gps(self, pos: Point) -> GPS:
 #       return self.pilot_position + self.rotation.inverse().transform_point(pos)
    

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
        self.transform_from = Transformation.build(-self.transform_to.translation,
                                             self.transform_to.rotation.conjugate())

    @staticmethod
    def home():
        """Default home is NWU"""
        return FlightLine(Coord.from_nothing(), Coord.from_zx(P0(), PZ(-1), PX()))

    @staticmethod
    def from_box(box: Box, world_home: GPS):
        """Constructor from a Box instance. This method assumes the input data is in the 
        Ardupilot default World frame (NED). It creates the contest frame from the box as described in __init__, 
        ie z up, y in the box heading direction. 

        Args:
            box (Box): box defining the contest coord
            world_home (GPS): home position of the input data

        Returns:
            FlightLine
        """
        return FlightLine(


            # this just sets x,y,z origin to zero and unit vectors = [1 0 0] [0 1 0] [0 0 1]
            Coord.from_zx(P0(), PZ(), PX()),
            Coord.from_yz(
                box.pilot_position - world_home,
                Point(np.cos(box.heading), np.sin(box.heading), 0),
                PZ(-1)
            )
        )

    @staticmethod
    def from_initial_position(flight):
        return FlightLine.from_box(Box.from_initial(flight), flight.origin)

    @staticmethod
    def from_heading(flight, heading: float):
        """generate a flightline based on the turn on gps position and a heading

        Args:
            flight (Flight): the flight to take the initial gps position from.
            heading (float): the direction towards centre in radians
        """

        return FlightLine.from_box(
            Box(
                'heading',
                GPS(
                    flight.data.iloc[0].global_position_latitude,
                    flight.data.iloc[0].global_position_longitude
                ),
                heading
            ))

    @staticmethod
    def from_covariance(flight):
        """generate a flightline from a flight based on the covariance matrix

        Args:
            flight (Flight):
        """
        return FlightLine.from_box(Box.from_covariance(flight), flight.origin)
