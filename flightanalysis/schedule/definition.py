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

class ManParm:
    """This class represents a parameter that can be used to characterise the geometry of a manoeuvre.
    For example, the loop diameters, line lengths, roll direction. 
    """
    def __init__(self, name:str, criteria: Union[Comparison, Combination], collectors: List[Callable], default=None):
        """Construct a ManParm

        Args:
            name (str): a short name, must work as an attribute so no spaces or funny characters
            criteria (Comparison): The comparison criteria function to be used when judging this parameter
            default (float): A default value (or default option if specified in criteria)
            collector (Callable): a list of functions that will pull values for this parameter from an Elements 
                collection. If the manoeuvre was flown correctly these should all be the same. The resulting list 
                can be passed through the criteria (Comparison callable) to calculate a downgrade.
        """
        self.name=name
        self.criteria = criteria
        self.default = default
        self.collectors = collectors

    def append(self, collector: Union[Callable, List[Callable]]):
        if isinstance(collector, Callable):
            self.collectors.append(collector)    
        else:
            for coll in collector:
                self.append(coll)

    def collect(self, els):
        return [collector(els) for collector in self.collectors]

    def get_downgrades(self, els):
        return self.criteria(*self.collect(els))

    @property
    def value(self):
        if isinstance(self.criteria, Comparison):
            return self.default
        elif isinstance(self.criteria, Combination):
            return self.criteria[self.default]


class ManParms:
    """This class wraps around a dict of ManParm. it provides attribute access to items based on their
    names and a constructer from a list of them (as the names are internal)
    """
    def __init__(self, parms:Dict[str, ManParm]):
        self.parms = parms
    
    def __getattr__(self, name):
        return self.parms[name].value

    @staticmethod
    def from_list(mps: List[ManParm]):
        return ManParms({mp.name: mp for mp in mps})

    def add(self, parm):
        self.parms[parm.name] = parm

    def collect(self, manoeuvre: Manoeuvre) -> Dict[str, float]:
        """Collect the comparison downgrades for each manparm for a given manoeuvre.

        Args:
            manoeuvre (Manoeuvre): The Manoeuvre to assess

        Returns:
            Dict[str, float]: The sum of downgrades for each ManParm
        """
        return {key: mp.get_downgrades(manoeuvre.elements) for key, mp in self.parms.items()}
    
    def append_collectors(self, colls: Dict[str, Callable]):
        """Append each of a dict of collector methods to the relevant ManParm

        Args:
            colls (Dict[str, Callable]): dict of parmname: collector method
        """
        for mp, col in colls.items():
            self.parms[mp].append(col)



def _a(arg):
    if isinstance(arg, Callable): 
        return arg
    elif isinstance(arg, ManDef):
        return lambda mps: mps[arg.name].value
    elif isinstance(arg, Number):
        return lambda mps: arg
    elif isinstance(arg, str): 
        return lambda mps: mps[arg].value



class ElDef:
    """This class creates a function to build an element (Loop, Line, Snap, Spin, Stallturn)
    based on a ManParms collection. 
    """
    def __init__(self, name, Kind, pfuncs: dict):
        """ElDef Constructor

        Args:
            name (_type_): the name of the Eldef, must be unique and work as an attribute
            Kind (_type_): the class of the element (Loop, Line etc)
            pfuncs (dict): the function to create the element from the ManParms collection. takes
                a ManParms as the only argument, returns the element.
        """
        self.name = name
        self.Kind = Kind
        self.pfuncs = pfuncs

    def __call__(self, mps: ManParms) -> El:
        kwargs = {pname: pfunc(mps) for pname, pfunc in self.pfuncs.items() }
        kwargs["uid"] = self.name
        return self.Kind(**kwargs) 
    
    def build(name, Kind, pfuncs):
        return ElDef(
            name, 
            Kind, 
            {k: _a(v) for k, v in pfuncs.items()}
        )

    @staticmethod
    def loop(name:str, s, r, angle, roll=0):
        return ElDef.build(name, Loop, dict(
            speed=s,
            radius=r,
            angle=angle,
            roll=roll
        ))
        
    @staticmethod        
    def line(name:str, s, l, roll=0):
        return ElDef.build(name, Line, dict(
            speed=s,
            length=l,
            roll=roll
        ))

    @staticmethod
    def roll(name: str, s, rate, angle):
        return ElDef.build(name, Line, dict(
            speed=s,
            length=lambda mps: rate * abs(angle) * s,
            roll=angle
        ))


class ElDefs:
    """This class wraps a dict of ElDefs, which would generally be used sequentially to build a manoeuvre.
    It provides attribute access to the ElDefs based on their names. 
    """
    def __init__(self, edefs: Dict[str, ElDef]):
        self.edefs = edefs

    def __getattr__(self, name):
        return self.edefs[name]

    @staticmethod
    def from_list(edfs: List[ElDef]):
        return ElDefs({ed.name: ed for ed in edfs})

    def __iter__(self):
        for ed in self.edefs.values():
            yield ed

    def __getitem__(self, name):
        return self.edefs.values()[name]


    def add(self, ed: ElDef) -> Dict[str, Callable]:
        """Add a new element definition to the collection. Returns the functions to retrieve
        the geometric parameters for this element from the elements dict

        Args:
            ed (ElDef): the new element definition

        Returns:
            Dict[str, Callable]: functions to retrieve the relevant parameters from the elements collection
        """
        self.edefs[ed.name] = ed

        def get_p_from_elm(els, pname):
            return getattr(els.els[ed.name], pname)

        return {pname: partial(get_p_from_elm, pname=pname) for pname in self.edefs[ed.name].Kind.parameters}


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