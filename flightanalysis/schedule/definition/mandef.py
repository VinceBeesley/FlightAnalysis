"""This module contains the structures used to describe the elements within a manoeuvre and
their relationship to each other. 

A Manoeuvre contains a dict of elements which are constructed in order. The geometry of these
elements is described by a set of high level parameters, such as loop radius, combined line 
length of lines, roll direction. 

A complete manoeuvre description includes a set of functions to create the elements based on
the higher level parameters and another set of functions to collect the parameters from the 
elements collection.
"""
import enum
from typing import List, Dict, Callable, Union
import numpy as np
import pandas as pd
from numbers import Number
from flightanalysis.schedule.elements import Loop, Line, Snap, Spin, StallTurn, El, Elements
from flightanalysis.schedule.manoeuvre import Manoeuvre
from flightanalysis.criteria.comparison import Comparison
from flightanalysis.criteria.local import Combination

from functools import partial

from . import ManParm, ManParms, ElDef, ElDefs, _a


class ManDef:
    """This is a class to define a manoeuvre for template generation and judging.

    It also contains lots of helper functions for creating elements and common combinations
    of elements
    """
    def __init__(self, name, mps:ManParms=ManParms({}), eds:ElDefs=ElDefs({})):
        self.name = name
        self.mps = mps
        self.eds = eds

    def create(self):
        return Manoeuvre(self.name, 2, Elements.from_list([ed(self.mps) for ed in self.eds]))

    def create_rolls(self, name, s, rolls: ManParm, rate, pause):
    

        l2_rolls = []
        l2_pauses = []
        for i, roll in range(len(rolls.value)):
            l2_rolls.append(self.add_roll(f"{name}2roll{i}", s, rate, roll))
            if not i == len(rolls)-1:
                l2_pauses.append(self.add_line(f"{name}2pause{i}", s, pause, 0))
        
        return dict(
            rate=None,
            speed=None,
            pause=None,
            rolls=None
        )

    def add_roll_centred(self, name: str, s, l, rolls, rate, pause, criteria):

        #a function to calculate the total length of the rolling elements
        rlength = lambda mp: _a(rate)(mp) * _a(s)(mp) * sum([abs(_a(roll)(mp)) for roll in rolls]) + _a(pause)(mp) * (len(rolls) - 1)
        
        #subtract from total length to get the length of the pads
        plength = lambda mp: 0.5 * (_a(l)(mp) - rlength(mp))

        #create the first pad
        l1 = self.add_line(name + "1", s, plength, 0)
        
        #create the rolls
        l2 = self.create_rolls(name + "2", s, rolls, rate, pause)
        #create the last pad
        l3 = self.add_line(name + "3", s, plength, 0)

        #create an internal ManParm to check the pad lengths
        self.mps.add(ManParm(f"{name}_pad", criteria, None, [l1["length"], l3["length"]]))

        #return the external ManParms
        all_ls = [l1, l2, l3]
        return dict(
            length=lambda els:  sum([l["length"](els) for l in all_ls]),
            rate = l2["rate"],
            speed = [l["speed"] for l in all_ls],
            pause = l2["pause"],
            rolls = l2["roll"]
        )


    @staticmethod
    def parse():
        pass