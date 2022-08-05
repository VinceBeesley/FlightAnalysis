"""This file contains some Enums and classes that could be used to set up a manoeuvre, for 
example containing the line before and scaling the ManParms so that it fills the box.

WIP, very vague ideas at the moment.

"""

from enum import Enum

class Orientation(Enum):
    DRIVEN=0
    UPRIGHT=1
    INVERTED=-1

class Direction(Enum):
    DRIVEN=0
    UPWIND=1
    DOWNWIND=2

class Height(Enum):
    DRIVEN=0
    BTM=1
    MID=2
    TOP=3

class Position(Enum):
    CENTRE=1
    END=2


class BoxLocation():
    def __init__(self, h: Height, d: Direction, o: Orientation):
        self.h = h
        self.d = d
        self.o = o

    @staticmethod
    def driven():
        return BoxLocation(Height.DRIVEN, Direction.DRIVEN, Orientation.DRIVEN)


class ManInfo:
    def __init__(self, name:str, short_name:str, k:float, start: BoxLocation, end: BoxLocation):
        self.name = name
        self.short_name = short_name
        self.k = k
        self.start = start
        self.end = end

        