from __future__ import annotations
from flightanalysis.state import State
from geometry import Point, Coord, Quaternion, PX, PY, PZ, P0, Transformation
import numpy as np
from dataclasses import dataclass
from typing import Union, Any


@dataclass()
class Measurement:
    value: Union[Point, Any]
    expected: Union[Point, Any]
    visibility: np.ndarray
        
    @staticmethod
    def vector_vis(value: Point, expected: Point, loc: Point, att: Quaternion) -> Measurement:
        return Measurement(value, expected, Measurement._vector_vis(value, loc)    )

    @staticmethod
    def _vector_vis(direction: Point, loc: Point) -> np.ndarray:
        #a vector error is more visible if it is perpendicular to the viewing vector
        # 0 to np.pi, pi/2 gives max, 0&np.pi give min
        return 1 - 0.8* np.abs(Point.cos_angle_between(loc, direction))

    @staticmethod
    def track_vis(value: Point, expected: Point, loc: Point, att: Quaternion) -> Measurement:
        return Measurement(value, expected, Measurement._track_vis(value, loc)    )

    @staticmethod
    def _track_vis(axis: Point, loc: Point) -> np.ndarray:
        #a track error is more visible if it is parrallel to the viewing vector
        # 0 to np.pi, pi/2 gives max, 0&np.pi give min
        return np.abs(Point.cos_angle_between(loc, axis))
    

    @staticmethod
    def roll_vis(value: Point, expected: Point, loc: Point, att: Quaternion) -> Measurement:
        return Measurement(value, expected, Measurement._roll_vis(loc, att))
    
    @staticmethod
    def _roll_vis(loc: Point, att: Quaternion) -> np.ndarray:
        #a roll error is more visible if the movement of the wing tips is perpendicular to the view vector
        #the wing tips move in the local body Z axis
        world_tip_movement_direction = att.transform_point(PZ()) 
        return 1-0.8*np.abs(Point.cos_angle_between(loc, world_tip_movement_direction))

    @staticmethod
    def speed(fl: State, tp: State, coord: Coord) -> Measurement:
        return Measurement.vector_vis(fl.vel, tp.vel, fl.pos, tp.att)
    
    @staticmethod
    def roll_angle(fl: State, tp: State, coord: Coord) -> Measurement:
        """vector in the body X axis, length is equal to the roll angle difference from template"""

        body_roll_error = Quaternion.body_axis_rates(tp.att, fl.att) * PX()
        world_roll_error = fl.att.transform_point(body_roll_error)
        return Measurement.roll_vis(world_roll_error, P0(len(world_roll_error)), fl.pos, tp.att)

    @staticmethod
    def roll_rate(fl: State, tp: State, coord: Coord) -> Measurement:
        """vector in the body X axis, length is equal to the roll rate"""
        return Measurement.roll_vis(
            fl.att.transform_point(fl.p * PX()), 
            tp.att.transform_point(tp.p * PX()),
            fl.pos, 
            tp.att
        )
    
    @staticmethod
    def track_y(fl: State, tp:State, coord: Coord) -> Measurement:
        """angle error in the velocity vector about the coord y axis"""
        tr = Transformation.from_coord(coord).q.inverse()

        flcvel = tr.transform_point(fl.att.transform_point(fl.vel)) 
        tpcvel = tr.transform_point(tp.att.transform_point(tp.vel))

        flycvel = Point(flcvel.x, flcvel.y, tpcvel.z)

        cyerr = (Point.cross(flycvel, tpcvel) / (abs(flycvel) * abs(tpcvel))).arcsin
        #cyerr = Point.vector_projection(cerr, PY())
        
        wyerr = tp.att.transform_point(cyerr)
        return Measurement.track_vis(wyerr, P0(len(wyerr)), tp.pos, tp.att)

    @staticmethod
    def track_z(fl: State, tp:State, coord: Coord) -> Measurement:
        tr = Transformation.from_coord(coord).q.inverse()

        flcvel = tr.transform_point(fl.att.transform_point(fl.vel)) 
        tpcvel = tr.transform_point(tp.att.transform_point(tp.vel)) 

        flzcvel = Point(flcvel.x, tpcvel.y, flcvel.z)

        czerr = (Point.cross(flzcvel, tpcvel) / (abs(flzcvel) * abs(tpcvel))).arcsin
        #czerr = Point.vector_projection(cerr, PZ())
        
        wzerr = tp.att.transform_point(czerr)
        return Measurement.track_vis(wzerr, P0(len(wzerr)), tp.pos, tp.att)

    @staticmethod
    def radius(fl:State, tp:State, coord:Coord) -> Measurement:
        """error in radius as a vector in the radial direction"""
        tprad = tp.pos - coord.origin
        rad = Point.vector_projection(fl.pos - coord.origin, tprad)
        return Measurement.vector_vis(rad, tprad, tp.pos, tp.att)
    