
from enum import Enum
from typing import List
import numpy as np


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


class ElType(Enum):
    NORMAL = 1
    SPIN = 2
    SNAP = 3
    STALLTURN = 4

class RollPosition(Enum):
    CENTRE = 0
    START = 1
    END = 2
    

class ElmDef():
    def __init__(
        self, 
        radius: str=None, 
        loops: float=0.0, 
        length: str=None,
        rolls: str=None, 
        rollpos: RollPosition=None,
        rollrate: str=None
    ):
        self.parms = []
        def addparm(name):
            self.parms.append(name)
            return name

        self.radius = addparm(radius)
        self.loops = loops
        self.length = addparm(length)
        self.rolls = rolls
        self.rollpos = rollpos
        self.rollrate = addparm(rollrate)

    @staticmethod
    def parse(radius, loops, length, rolls, rollpos, rollrate):
        parg = lambda arg: None if arg=="-" else arg
        rpos = lambda rpos: RollPosition[rpos] if rpos else None
        return ElmDef(
            parg(radius), 
            float(parg(loops)),
            parg(length),
            parg(rolls),
            rpos(parg(rollpos)),
            parg(rollrate)
        )

    


class ManDef():
    def __init__(self, name:str, k:int, start:BoxLocation, end:BoxLocation, pos: Position, posel: str, elms: List[ElmDef]):
        self.name = name
        self.k = k
        self.start = start
        self.end = end
        self.elms = elms
        self.pos= pos
        self.posel = posel

    @staticmethod
    def parse(name, k, entry, direction, start_height, end_height, pos, posel, *elments):
        return ManDef(
            name=name, 
            k=int(k),
            start=BoxLocation(Height[start_height], Direction[direction], Orientation[entry]),
            end=BoxLocation(Height[end_height], Direction.DRIVEN, Orientation.DRIVEN),
            pos=Position[pos],
            posel=int(posel),
            elms=[ElmDef.parse(*el) for el in elments]
        )

class SchedDef():
    def __init__(self, name, category, defs: List[ManDef]):
         self.name = name
         self.category = category
         self.defs = defs

    @staticmethod
    def parse(file: str):
        with open(file, 'r') as f:
            lines = [l.strip().split("#")[0].split() for l in f.readlines()]
            lines = [l for l in lines if len(l) > 0]
        
        mdata = []
        for l in lines[1:]:
            
            if l[0] == "MANOEUVRE":
                mdata.append([])
            else:
                mdata[-1].append(l)

        return SchedDef(lines[0][0], lines[0][1], [ManDef.parse(*man[0] + man[1:]) for man in mdata])