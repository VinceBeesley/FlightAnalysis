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
from flightanalysis.criteria.comparison import Comparison, hard_zero
from functools import partial

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
            collector (Callable): a list of functions that will pull values for this parameter from an Elements 
                collection. If the manoeuvre was flown correctly these should all be the same. The resulting list 
                can be passed through the criteria (Comparison callable) to calculate a downgrade.
        """
        self.name=name
        self.criteria = criteria
        self.value = value
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


def _a(arg):
    """Ths checks the arguments to the ManDef helper methods and returns the correct 
    type of lambda"""
    if isinstance(arg, str): 
        return lambda mp: mp.parms[arg].value
    elif isinstance(arg, Number):
        return lambda mp: arg
    elif isinstance(arg, Callable): 
        return arg
    else:
        raise TypeError("Unknown argument ManDef helper method argument received")


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

    def add_loop(self, name:str, s, r, angle, roll):
        return self.eds.add(ElDef(name, Loop, dict(
            speed=_a(s),
            radius=_a(r),
            angle=_a(angle),
            roll=_a(roll)
        )))
        
    def add_line(self, name:str, s, l, roll):
        return self.eds.add(ElDef(name, Line, dict(
            speed=_a(s),
            length=_a(l),
            roll=_a(roll)
        )))

    def add_roll(self, name: str, s, rate, angle, direction):
        return self.eds.add(ElDef(name, Line, dict(
            speed=_a(s),
            length=lambda mp: _a(rate)(mp) * \
                abs(_a(angle)(mp)) * \
                    _a(s)(mp),
            roll=lambda mp: _a(angle)(mp) * _a(direction)(mp)
        )))

    def add_roll_centred(self, name: str, s, l, rate, direction, pause, rolls, criteria):

        rlength = lambda mp: _a(rate)(mp) * _a(s)(mp) * sum([abs(_a(roll)(mp)) for roll in rolls]) + _a(pause)(mp) * (len(rolls) - 1)
        
        plength = lambda mp: 0.5 * (_a(l)(mp) - rlength(mp))
      
        l1 = self.add_line(name + "1", s, plength, 0)

        l2_rolls = []
        l2_pauses = []
        for i, roll in enumerate(rolls):
            l2_rolls.append(self.add_roll(f"{name}2roll{i}", s, rate, roll, direction))
            if not i == len(rolls)-1:
                l2_pauses.append(self.add_line(f"{name}2pause{i}", s, pause, 0))

        l3 = self.add_line(name + "3", s, plength, 0)

        self.mps.add(ManParm(f"{name}_pad", criteria, None, [l1["length"], l3["length"]]))



        self.mps.add(ManParm(
            f"{name}roll_directions", 
            hard_zero, 
            None, 
            [lambda els: np.sign(r) * l2r["direction"](els)   for r, l2r in zip(rolls, l2_rolls)]
        ))  # TODO this isn't working, need to use functools.partial

        all_ls = l2_rolls + l2_pauses + [l1, l3]
        return dict(
            length=lambda els:  sum([l["length"](els) for l in all_ls]),
            rate = [l["rate"] for l in  l2_rolls],
            direction = [lambda els: l["direction"](els) * np.sign(r)  for r, l in zip(rolls, l2_rolls)],
            speed = [l["speed"] for l in all_ls],
            pause = [l["length"] for l in l2_pauses]
        )


    @staticmethod
    def parse():
        pass