"""This file contains some Enums and classes that could be used to set up a manoeuvre, for 
example containing the line before and scaling the ManParms so that it fills the box.

WIP, very vague ideas at the moment.

"""
import numpy as np
from geometry import Point, Transformation, Euler
from enum import Enum

class Orientation(Enum):
    DRIVEN=0
    UPRIGHT=1
    INVERTED=-1

    def roll_angle(self):
        try:
            return {
                1: np.pi,
                -1: 0
            }[self.value]
        except KeyError:
            raise ValueError("Cant calculate yaw angle for driven Orientation")

class Direction(Enum):
    DRIVEN=0
    UPWIND=1
    DOWNWIND=-1

    def yaw_angle(self, wind: int=1) -> float:
        try:
            return {
                1: np.sign(wind),
                -1: 0
            }[self.value]
        except KeyError:
            raise ValueError("Cant calculate yaw angle for driven Direction")


class Height(Enum):
    BTM=1
    MID=2
    TOP=3

    def calculate(self, depth):
        top = np.tan(np.radians(60))* depth
        btm = np.tan(np.radians(15))* depth
    
        return {
            1: btm ,
            2: 0.5 * (btm + top),
            3: top
        }[self.value]
        
class Position(Enum):
    CENTRE=0
    END=1


class BoxLocation():
    def __init__(
        self, 
        h: Height, 
        d: Direction=Direction.DRIVEN, 
        o: Orientation=Orientation.DRIVEN
    ):
        self.h = h
        self.d = d
        self.o = o
    

class ManInfo:
    def __init__(
        self, 
        name:str, 
        short_name:str, 
        k:float, 
        position: Position,
        start: BoxLocation, 
        end: BoxLocation,
    ):

        self.name = name
        self.short_name = short_name
        self.k = k
        self.position=position
        self.start = start
        self.end = end

    def initial_transform(self, depth=170, wind=1) -> Transformation:
        return Transformation(
            Point(
                {
                    Position.CENTRE: {
                        Direction.UPWIND: -depth * np.tan(np.radians(60)),
                        Direction.DOWNWIND: depth * np.tan(np.radians(60))
                    }[self.start.d],
                    Position.END: 0.0
                }[self.position],
                depth,
                self.start.h.calculate(depth)
            ), 
            Euler(
                self.start.o.roll_angle(),
                0.0,
                self.start.d.yaw_angle(wind)
            )
        )


        