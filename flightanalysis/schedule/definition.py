"""This module contains the structures used to describe the elements within a manoeuvre and
their relationship to each other. 

A Manoeuvre contains a dict of elements which are constructed in order. The geometry of these
elements is described by a set of high level parameters, such as loop radius, combined line 
length of lines, roll direction. 

A complete manoeuvre description includes a set of functions to create the elements based on
the higher level parameters and another set of functions to collect the parameters from the 
elements collection.
"""
from typing import List, Dict, Callable, Union
import numpy as np
import pandas as pd
from numbers import Number
from flightanalysis.schedule.elements import Loop, Line, Snap, Spin, StallTurn, El
from flightanalysis.schedule.manoeuvre import Manoeuvre
from flightanalysis.criteria.comparison import Comparison


class ManParm:
    """This class represents a parameter that can be used to characterise the geometry of a manoeuvre.
    For example, the loop diameters, line lengths, roll direction. 
    """
    def __init__(self, name:str, criteria: Comparison, value: float, collectors: List[Callable]):
        """Construct a ManParm

        Args:
            name (str): a short name, must work as an attribute so no spaces or funny characters
            criteria (Comparison): The comparison criteria function to be used when judging this parameter
            value (float): A default value, perhaps remove this it might cause more harm than convenience
            collector (Callable): a function that will pull a list of values for this parameter from the ElDefs collection. 
                If the manoeuvre was flown correctly these should all be the same. The resulting list can be 
                passed through the criteria (Comparison callable) to calculate a downgrade.
        """
        self.name=name
        self.criteria = criteria
        self.value = value
        self.collectors = collectors

    def append(self, collector):
        self.collectors.append(collector)    

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
        """Add a new element definition to the collection. Returns a the functions to retrieve
        the geometric parameters for this element from the elements dict

        Args:
            ed (ElDef): the new element definition

        Returns:
            Dict[str, Callable]: functions to retrieve the relevant parameters from the elements collection
        """
        self.edefs[ed.name] = ed
        return {pname: lambda els: getattr(els[ed.name], pname) 
        for pname in self.edefs[ed.name].Kind.parameters}




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
        return Manoeuvre(self.name, 2, [ed(self.mps) for ed in self.eds])

    @staticmethod
    def _arg_check(arg):
        if isinstance(arg, str): 
            return lambda mp: mp.parms[arg]
        elif isinstance(arg, Number):
            return lambda mp: arg
        elif isinstance(arg, Callable): 
            return arg

    def add_loop(self, name:str, s, r, angle, roll):
        return self.eds.add(ElDef(name, Loop, dict(
            speed=ManDef._arg_check(s),
            radius=ManDef._arg_check(r),
            angle=ManDef._arg_check(angle),
            roll=ManDef._arg_check(roll)
        )))
        
    def add_line(self, name:str, s, l, roll):
        return self.eds.add(ElDef(name, Line, dict(
            speed=ManDef._arg_check(s),
            length=ManDef._arg_check(l),
            roll=ManDef._arg_check(roll)
        )))

    def add_roll(self, name: str, s, rate, angle):
        return self.eds.add(ElDef(name, Line.from_roll, dict(
            speed=ManDef._arg_check(s),
            rate=ManDef._arg_check(rate),
            angle=ManDef._arg_check(angle)
        )))

    def add_roll_centred(self, name: str, s, l, rate, roll):
       
        plength = lambda mp: 0.5 * mp.parms[l] - mp.parms[rate] * np.pi * mp.parms[s]
        
        l1 = self.add_line(name + "1", s, plength, 0)
        l2 = self.add_roll(name + "2", s, rate, roll)
        l3 = self.add_line(name + "3", s, plength, 0)

        return dict(
            length=lambda els: els[name + "1"].length + els[name + "2"].length + els[name + "3"].length,
            pad_length = [lambda els: els[name + "1"].length, lambda els: els[name + "2"].length]
            rate = l2["rate"],
            direction = l2["direction"],
            roll = l2["roll"]
        )
