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

    def to_dict(self):
        return dict(
            value = self.value.to_dicts() if isinstance(self.value, Point) else list(self.value),
            expected = self.expected.to_dicts() if isinstance(self.expected, Point) else list(self.expected),
            visibility = list(self.visibility)
        )
    
    def exit_only(self):
        fac = np.zeros(len(self.value))
        fac[-1] = 1
        return Measurement(
            self.value * fac,
            self.expected * fac,
            self.visibility * fac
        )

    @staticmethod
    def from_dict(data) -> Measurement:
        return Measurement(
            Point(**data['value']) if isinstance(data['value'], dict) else np.array(data['value']),
            Point(**data['expected']) if isinstance(data['expected'], dict) else np.array(data['expected']),
            np.array(data['visibility'])
        )

    def _pos_vis(loc: Point):
        return loc.y / abs(loc)

    @staticmethod
    def vector_vis(value: Point, expected: Point, loc: Point, att: Quaternion) -> Measurement:
        return Measurement(
            value, expected, 
            Measurement._vector_vis(value, loc) * Measurement._pos_vis(loc)
        )

    @staticmethod
    def _vector_vis(direction: Point, loc: Point) -> np.ndarray:
        #a vector error is more visible if it is perpendicular to the viewing vector
        # 0 to np.pi, pi/2 gives max, 0&np.pi give min
        return 1 - 0.8* np.abs(Point.cos_angle_between(loc, direction))

    @staticmethod
    def track_vis(value: Point, expected: Point, loc: Point, att: Quaternion) -> Measurement:
        return Measurement(
            value, expected, 
            Measurement._track_vis(value, loc) * Measurement._pos_vis(loc)
        )

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
    def speed(fl: State, tp: State, ref_frame: Transformation) -> Measurement:
        return Measurement.vector_vis(fl.vel, tp.vel, fl.pos, tp.att)
    
    @staticmethod
    def roll_angle(fl: State, tp: State, ref_frame: Transformation) -> Measurement:
        """vector in the body X axis, length is equal to the roll angle difference from template"""

        body_roll_error = Quaternion.body_axis_rates(tp.att, fl.att) * PX()
        world_roll_error = fl.att.transform_point(body_roll_error)
        return Measurement.roll_vis(world_roll_error, P0(len(world_roll_error)), fl.pos, tp.att)

    @staticmethod
    def roll_rate(fl: State, tp: State, ref_frame: Transformation) -> Measurement:
        """vector in the body X axis, length is equal to the roll rate"""
        return Measurement.roll_vis(
            fl.att.transform_point(fl.p * PX()), 
            tp.att.transform_point(tp.p * PX()),
            fl.pos, 
            tp.att
        )
    
    @staticmethod
    def track_y(fl: State, tp:State, ref_frame: Transformation) -> Measurement:
        """angle error in the velocity vector about the coord y axis"""
        tr = ref_frame.q.inverse()

        flcvel = tr.transform_point(fl.att.transform_point(fl.vel)) 
        tpcvel = tr.transform_point(tp.att.transform_point(tp.vel))

        flycvel = Point(flcvel.x, flcvel.y, tpcvel.z)

        cyerr = (Point.cross(flycvel, tpcvel) / (abs(flycvel) * abs(tpcvel))).arcsin
        #cyerr = Point.vector_projection(cerr, PY())
        
        wyerr = tp.att.transform_point(cyerr)
        return Measurement.track_vis(wyerr, P0(len(wyerr)), tp.pos, tp.att)

    @staticmethod
    def track_z(fl: State, tp:State, ref_frame: Transformation) -> Measurement:
        tr = ref_frame.q.inverse()

        flcvel = tr.transform_point(fl.att.transform_point(fl.vel)) 
        tpcvel = tr.transform_point(tp.att.transform_point(tp.vel)) 

        flzcvel = Point(flcvel.x, tpcvel.y, flcvel.z)

        czerr = (Point.cross(flzcvel, tpcvel) / (abs(flzcvel) * abs(tpcvel))).arcsin
        #czerr = Point.vector_projection(cerr, PZ())
        
        wzerr = tp.att.transform_point(czerr)
        return Measurement.track_vis(wzerr, P0(len(wzerr)), tp.pos, tp.att)

    @staticmethod
    def radius(fl:State, tp:State, ref_frame: Transformation) -> Measurement:
        """error in radius as a vector in the radial direction"""
        tprad = tp.arc_centre() # body frame vector to centre of loop
        flrad = fl.arc_centre() 

        fl_loop_centre = fl.body_to_world(flrad)  # centre of loop in world frame
        tp_loop_centre = tp.body_to_world(tprad)  

        fl_loop_centre_lc = ref_frame.att.inverse().transform_point(fl_loop_centre - ref_frame.pos)
        tp_loop_centre_lc = ref_frame.att.inverse().transform_point(tp_loop_centre - ref_frame.pos)

        #figure out whether its a KE loop
        loop_plane = PY()
        tp_lc = tp.move_back(ref_frame)
        fl_lc = fl.move_back(ref_frame)
        if (tp_lc.y.max() - tp_lc.y.min()) > (tp_lc.z.max() - tp_lc.z.min()):
            loop_plane = PZ()
        
        fl_rad_lc = Point.vector_rejection(fl_loop_centre_lc, loop_plane) - fl_lc.pos #loop frame radius vector
        tp_rad_lc = Point.vector_rejection(tp_loop_centre_lc, loop_plane) - tp_lc.pos

        return Measurement.vector_vis(
            ref_frame.att.transform_point(fl_rad_lc), 
            ref_frame.att.transform_point(tp_rad_lc), 
            tp.pos, tp.att
        )
    