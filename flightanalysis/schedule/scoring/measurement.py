from __future__ import annotations
from flightanalysis.state import State
from geometry import Point, Coord, Quaternion, PX, PY, PZ
import numpy as np


class Measurement:
    def __init__(self, measure: Point, visibility: np.array):
        self.measure = measure
        self.visibility = visibility
        self.reading = abs(self.measure) * self.visibility
    
    @staticmethod
    def vector_vis(measure: Point, loc: Point, att: Quaternion) -> Measurement:
        #a vector error is more visible if it is perpendicular to the viewing vector
        visability = np.abs(Point.cos_angle_between(loc, measure))  # 0 to np.pi, pi/2 gives max, 0&np.pi give min
        return Measurement(measure, visability)

    @staticmethod
    def angle_vis(measure: Point, loc: Point, att: Quaternion) -> Measurement:
        #a roll error is more visible if the movement of the wing tips is perpendicular to the view vector
        #the wing tips move in the local body Z axis
        world_tip_movement_direction = att.inverse().transform_point(PZ()) 
        visability = np.abs(Point.cos_angle_between(loc, world_tip_movement_direction))
        return Measurement(measure, visability)
            
    @staticmethod
    def speed_ratio(fl: State, tp: State, coord: Coord) -> Measurement:
        return Measurement.vector_vis(fl.vel, fl.pos, tp.att)
    
    @staticmethod
    def roll_angle(fl: State, tp: State, coord: Coord) -> Measurement:
        body_roll_error = Quaternion.body_axis_rates(tp.att, fl.att)
        world_roll_error = fl.att.inverse().transform_point(body_roll_error * PX())
        return Measurement.angle_vis(world_roll_error, fl.pos, tp.att)

    @staticmethod
    def roll_rate(fl: State, tp: State, coord: Coord) -> Measurement:
        world_roll_rate = fl.att.inverse().transform_point(fl.p * PX())
        return Measurement.angle_vis(world_roll_rate, fl.pos, tp.att)
    
    @staticmethod
    def track(fl: State, tp:State, coord: Coord) -> Measurement:
        norm = Point.cross(fl.vel, tp.vel) * Point.angle_between(fl.vel, tp.vel)
        return Measurement.angle_vis(norm, tp.pos, tp.att)

    @staticmethod
    def track_y(fl: State, tp:State, coord: Coord) -> Measurement:
        norm = Point.cross(fl.vel, tp.vel) * Point.angle_between(fl.vel, tp.vel)
        normy = Point.vector_projection(norm, coord.y)
        return Measurement.angle_vis(normy, tp.pos, tp.att)

    @staticmethod
    def track_xz(fl: State, tp: State, coord: Coord) -> Measurement:
        pass

    @staticmethod
    def radius(fl:State, tp:State, coord:Coord) -> Measurement:
        rad = Point.vector_projection(fl.pos - coord.origin, tp.pos - coord.origin)
        return Measurement.vector_vis(rad, tp.pos, tp.att)
    
    