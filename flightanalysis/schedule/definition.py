
from typing import List, Dict, Callable
import numpy as np
import pandas as pd

from flightanalysis.schedule.elements import Loop, Line, Snap, Spin, StallTurn, El
from flightanalysis.criteria.comparison import Comparison


class ManParm:
    """This class represents a parameter that can be used to characterise the geometry of a manoeuvre.
    For example, the loop diameters, line lengths, roll direction. 
    """
    def __init__(self, name:str, criteria: Comparison, value: float, collector: Callable):
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
        self.collector = collector
        

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
        return self.kind(**kwargs) 



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
        for ed in self.edfs:
            yield ed

    def __getitem__(self, name):
        return self.edefs.values()[name]


class ManDef:
    """This is a class to define a manoeuvre for template generation and judging.
    """
    def __init__(self, name, mps:ManParms, eds:ElDefs):
        self.name = name
        self.mps = mps
        self.eds = eds

    def create_elements(self):
        return [ed(self.mps) for ed in self.eds]
        

