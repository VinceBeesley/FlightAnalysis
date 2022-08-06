import enum
from typing import List, Dict, Callable, Union
import numpy as np
import pandas as pd
from numbers import Number
from flightanalysis.schedule.elements import Loop, Line, Snap, Spin, StallTurn, El, Elements
from flightanalysis.schedule.manoeuvre import Manoeuvre
from flightanalysis.criteria.comparison import Comparison
from flightanalysis.criteria.local import Combination
from inspect import getfullargspec
from functools import partial
from . import ManParm, ManParms, _a
from copy import deepcopy


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
        kwargs = {}
        args = getfullargspec(self.Kind.__init__).args
        for pname, pfunc in self.pfuncs.items():
            # only use the parameter if it is actually needed to create the element
            if pname in args: 
                kwargs[pname] = pfunc(mps)
        return self.Kind(uid=self.name, **kwargs) 
    
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

    def rename(self, new_name):
        return ElDef(new_name, self.Kind, self.pfuncs)

    @staticmethod
    def loop(name:str, ke, s, r, angle, roll):
        return ElDef.build(
            name, 
            Loop, 
            speed=s,
            radius=r,
            angle=angle,
            roll=roll,
            ke=lambda mps: ke
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

    @staticmethod
    def snap(name: str, s, rate, roll, direction):
        #The only way to work out the length of the snap is to create a template
        #and measure it, as it is a bit complicated and not used in the constructor. 
        # Therefore we bodge an extra pfunc onto the ElDef to do this. The pfuncs 
        # are only used if they are needed so it doesn't give an argument error.
        return ElDef.build(
            name,
            Snap,
            speed=s,
            rolls=roll,
            direction=direction,
            rate=rate,
            length=lambda mps: Snap(_a(s)(mps), _a(roll)(mps), _a(rate)(mps), 1, "temp").length
        )

    @staticmethod
    def spin(name: str, s, turns, opp_turns, rate):
        return ElDef.build(
            name,
            Spin,
            speed=s,
            turns=turns,
            opp_turns=opp_turns,
            rate=rate
        )

    @staticmethod
    def stallturn(name, s, rate):
        return ElDef.build(
            name,
            StallTurn,
            speed=s,
            yaw_rate=rate
        )

    @property
    def id(self):
        return int(self.name.split("_")[1])

class ElDefs:
    """This class wraps a dict of ElDefs, which would generally be used sequentially to build a manoeuvre.
    It provides attribute access to the ElDefs based on their names. 
    """
    def __init__(self, edefs: Dict[str, ElDef]=None):
        self.edefs = {} if edefs is None else edefs

    def __getattr__(self, name):
        if name in self.edefs:
            return self.edefs[name]

    @staticmethod
    def from_list(edfs: List[ElDef]):
        return ElDefs({ed.name: ed for ed in edfs})

    def __iter__(self):
        for ed in self.edefs.values():
            yield ed

    def __getitem__(self, name):
        return list(self.edefs.values())[name]

    def get_new_name(self):
        new_id = 0 if len(self.edefs) == 0 else list(self.edefs.values())[-1].id + 1
        return f"e_{new_id}"

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

    @staticmethod
    def create_roll_combo(name: str, rolls: ManParm, s, rates, pause):
        eds = ElDefs()
        
        for i in range(rolls.n):

            new_roll = eds.add(ElDef.roll(
                f"{name}_{i+1}",
                s,
                rates[i],
                rolls.valuefunc(i)
            ))

            rolls.append(new_roll.collectors["roll"])
            
            if i < rolls.n - 1 and np.sign(rolls.value[i]) == np.sign(rolls.value[i+1]):
                eds.add(ElDef.line(
                    f"{name}_{i+1}_pause",
                    s, pause, 0
                ))
            
        return eds

    def builder_list(self, name):
        return [e.pfuncs[name] for e in self if name in e.pfuncs]

    def builder_sum(self, name):
        return lambda mps : sum(b(mps) for b in self.builder_list(name))

    def collector_list(self, name):
        return [e.collectors[name] for e in self if name in e.collectors]

    def collector_sum(self, name):
        return lambda els : sum(c(els) for c in self.collector_list(name))
    