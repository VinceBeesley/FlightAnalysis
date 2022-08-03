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
    def __init__(self, name, mps:ManParms=ManParms(), eds:ElDefs=ElDefs()):
        self.name = name
        self.mps = mps
        self.eds = eds

    def create(self):
        return Manoeuvre(self.name, 2, Elements.from_list([ed(self.mps) for ed in self.eds]))


    def create_roll_combo(self, name: str, s, l, rolls, rate, pause, no_roll, criteria):
        rlengths = [
            lambda mps: rolls.valuefunc(i)(mps) * _a(s)(mps) / _a(rate)(mps) 
            for i in range(rolls.n)
        ]

        pad_length = lambda mps: 0.5*(_a(l)(mps) - sum(rl(mps) for rl in rlengths) - _a(pause)(mps) * (rolls.n - 1) )
        
        l1 = self.eds.add(ElDef.line(f"{name}_0", s, pad_length, no_roll))

        r_els = []
        p_els = []

        for i in range(rolls.n):
            r_els.append(self.eds.add(ElDef.roll(
                f"{name}_1_r{i}",
                s,
                rate,
                rolls.valuefunc(i)
            )))
            
            if i < rolls.n-1:
                p_els.append(self.eds.add(ElDef.line(
                    f"{name}_1_p{i}",
                    s, pause, no_roll
                )))
        
        l3 = self.eds.add(ElDef.line(f"{name}_1", s, pad_length, no_roll))

        #create a ManParm to check the pad lengths
        self.mps.add(ManParm(f"{name}_pad", criteria, None, [l1.collectors["length"], l3.collectors["length"]]))

        l.append(lambda els: sum([l.collectors["length"](els) for l in [l1, l3] + r_els + p_els]))
        rolls.append([rel.collectors["roll"] for rel in r_els])

        return [l1] + r_els + p_els + [l3]