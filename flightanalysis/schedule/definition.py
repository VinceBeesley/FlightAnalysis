
from enum import Enum
from tkinter import CENTER
from typing import List
import numpy as np
import pandas as pd
from pytest import param
from flightanalysis.schedule.elements import Loop, Line, Snap, Spin, StallTurn, El
from flightanalysis.criteria.comparison import Comparison
from collections.abc import Iterable

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



class ManDef():
    def __init__(
        self, 
        name:str, 
        k:int, 
        start:BoxLocation,  
        pos: Position, 
        posel: int, 
        generator: callable,
        comparer: callable
        ):
        self.name = name
        self.k = k
        self.start = start
        self.pos= pos
        self.posel = posel
        self.generator = generator
        self.comparer = comparer
        
    @staticmethod
    def compile_elms(*args):

        elms = []
        def append_els(arg):
            if isinstance(arg, El):
                elms.append(arg) 
            elif isinstance(arg, Iterable):
                for a in arg:
                    append_els(a)
            else:
                raise TypeError("expected a list or an El")

        append_els(args)

        return elms

        



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