from __future__ import annotations
from flightanalysis.state import State
from geometry import Point, Coord, Quaternion, PX, PY, PZ, P0
import numpy as np


class Measurement:
    def __init__(self, value: Point, expected: Point, visibility: np.array):
        self.value = value
        self.expected = expected
        self.visibility = visibility
    
    def __repr__(self) -> str:
        return f"Measurement(max={max(abs(self.value))}, min={min(abs(self.value))}, visibility={self.visibility.mean()}"

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
    def track(fl: State, tp:State, coord: Coord) -> Measurement:
        """angle error between fl and tp velocity vectors"""
        error = Point.cross(fl.vel, tp.vel).unit() * Point.angle_between(fl.vel, tp.vel)
        world_error = fl.att.inverse().transform_point(error)
        return Measurement.track_vis(world_error, P0(len(world_error)), tp.pos, tp.att)

    @staticmethod
    def ip_track(fl: State, tp:State, coord: Coord) -> Measurement:
        """angle error in the velocity vector about the coord y axis"""
        norm = Point.cross(fl.vel, tp.vel).unit() * Point.angle_between(fl.vel, tp.vel)
        normy = Point.vector_projection(norm, coord.y_axis)
        return Measurement.track_vis(normy, P0(len(normy)), tp.pos, tp.att)

    @staticmethod
    def op_track(fl: State, tp:State, coord: Coord) -> Measurement:
        """angular error in the velocity vector, due to deviations in the coord z axis"""
        z_dev = Point.vector_projection(fl.vel, coord.z_axis)
        opvel = tp.vel + z_dev
        error = Point.cross(opvel, tp.vel).unit() * Point.angle_between(opvel, tp.vel)
        world_error = fl.att.transform_point(error)
        return Measurement.track_vis(world_error, P0(len(world_error)), tp.pos, tp.att)

    @staticmethod
    def radius(fl:State, tp:State, coord:Coord) -> Measurement:
        """error in radius as a vector in the radial direction"""
        tprad = tp.pos - coord.origin
        rad = Point.vector_projection(fl.pos - coord.origin, tprad)
        return Measurement.vector_vis(rad, tprad, tp.pos, tp.att)
    