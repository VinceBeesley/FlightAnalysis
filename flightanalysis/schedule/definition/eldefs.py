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
from . import ManParm, ManParms, _a


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

