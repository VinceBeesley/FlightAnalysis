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

    The eldef also contains a set of collectors. These are a dict of str:callable pairs
    that collect the relevant parameter for this element from an Elements collection.
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

        
        self.collectors = {}
        for pname in self.Kind.parameters:
            #The collectors call Els.get_parameter_from_element and only need the self parameter
            self.collectors[pname] = partial(
                Elements.get_parameter_from_element, 
                element_name=self.name,
                parameter_name=pname
            )

    def __call__(self, mps: ManParms) -> El:
        kwargs = {pname: pfunc(mps) for pname, pfunc in self.pfuncs.items() }
        kwargs["uid"] = self.name
        return self.Kind(**kwargs) 
    
    def build(name, Kind, **kwargs):
        ed = ElDef(
            name, 
            Kind, 
            {k: _a(v) for k, v in kwargs.items()}
        )
        
        for key, value in kwargs.items():
            if isinstance(value, ManParm):
                value.append(ed.collectors[key])
            
        
        return ed

    @staticmethod
    def loop(name:str, s, r, angle, roll):
        return ElDef.build(
            name, 
            Loop, 
            speed=s,
            radius=r,
            angle=angle,
            roll=roll
        )
        
    @staticmethod        
    def line(name:str, s, l, roll):
        return ElDef.build(
            name, 
            Line, 
            speed=s,
            length=l,
            roll=roll
        )

    @staticmethod
    def roll(name: str, s, rate, angle):
        ed = ElDef.line(
            name, 
            s,
            lambda mps: abs(_a(angle)(mps)) * _a(s)(mps) / _a(rate)(mps),  
            angle
        )
        if isinstance(rate, ManParm):
            rate.append(ed.collectors["rate"])
        return ed


class ElDefs:
    """This class wraps a dict of ElDefs, which would generally be used sequentially to build a manoeuvre.
    It provides attribute access to the ElDefs based on their names. 
    """
    def __init__(self, edefs: Dict[str, ElDef]={}):
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


    def add(self, ed: Union[ElDef, List[ElDef]]) -> Union[ElDef, List[ElDef]]:
        """Add a new element definition to the collection. Returns the ElDef

        Args:
            ed (Union[ElDef, List[ElDef]]): The ElDef or list of ElDefs to add

        Returns:
            Union[ElDef, List[ElDef]]: The ElDef or list of ElDefs added
        """
        if isinstance(ed, ElDef):
            self.edefs[ed.name] = ed
            return ed
        else:
            return [self.add(e) for e in ed]
        


        