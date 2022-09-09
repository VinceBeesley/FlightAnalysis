import enum
from typing import List, Dict, Callable, Union
import numpy as np
import pandas as pd
from numbers import Number
from flightanalysis.schedule.elements import Loop, Line, Snap, Spin, StallTurn, El, Elements
from flightanalysis.schedule.manoeuvre import Manoeuvre
from flightanalysis.criteria import *
from flightanalysis import State
from functools import partial
from flightanalysis.base.collection import Collection

class MPOpp:
    def __init__(self, a, b, opp:str):
        assert opp in ["+", "-", "*", "/"]
        self.a = a
        self.b = b
        self.opp = opp

    def __call__(self, mps):
        return {
            '+': self.get_vf[self.a](mps) + self.get_vf[self.b](mps),
            '-': self.get_vf[self.a](mps) - self.get_vf[self.b](mps),
            '*': self.get_vf[self.a](mps) * self.get_vf[self.b](mps),
            '/': self.get_vf[self.a](mps) / self.get_vf[self.b](mps)
        }[self.opp]

    def get_vf(self, arg):
        if isinstance(arg, str):
            return lambda mps: mps[self.a].value
        elif isinstance(arg, self.__class__):
            return lambda mps: arg(mps)
        elif isinstance(arg, Number):
            return lambda mps: arg

    def _argcheck(self, arg):
        if isinstance(arg, ManParm):
            return arg.name
        else:
            return arg
        
    def __str__(self):
        return f"({str(self.a)}{self.opp}{str(self.b)})"



class ManParm:
    """This class represents a parameter that can be used to characterise the geometry of a manoeuvre.
    For example, the loop diameters, line lengths, roll direction. 
    """
    def __init__(self, name:str, criteria: Union[Criteria, Comparison, Combination], default=None, collectors: List[Callable]=None):
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
        
        self.collectors = [] if collectors is None else collectors
        self.n = len(self.criteria.desired[0]) if isinstance(self.criteria, Combination) else None
    
    def append(self, collector: Union[Callable, List[Callable]]):
        if isinstance(collector, Callable):
            self.collectors.append(collector)    
        else:
            for coll in collector:
                self.append(coll)

    def collect(self, els):
        return np.array([collector(els) for collector in self.collectors])

    def get_downgrades(self, els):
        return self.criteria(self.name, self.collect(els))

    @property
    def value(self):
        if isinstance(self.criteria, Comparison):
            return self.default
        elif isinstance(self.criteria, Combination):
            return self.criteria[self.default]

    def valuefunc(self, id:int=0) -> Callable:
        """Create a function to return the value property of this manparm from a manparms collection.
        
        Args:
            id (int, optional): The element id to return if reading the default from a Combination
            criteria. Defaults to 0.

        Raises:
            Exception: If some unknown criteria is being used

        Returns:
            Callable: function to get the default value for this manparm from the mps collection
        """
        if isinstance(self.criteria, Comparison) or isinstance(self.criteria, Criteria):
            return lambda mps: mps.data[self.name].value 
        elif isinstance(self.criteria, Combination):
            return lambda mps: mps.data[self.name].value[id] 
            #return partial(
            #   lambda mps, i: mps.parms[self.name].value[i], 
            #   i=id
            # )
        else:
            raise Exception("Cant create a valuefunc in this case")
        

class ManParms(Collection):
    VType=ManParm
    uid="name"

    def collect(self, manoeuvre: Manoeuvre) -> Dict[str, float]:
        """Collect the comparison downgrades for each manparm for a given manoeuvre.

        Args:
            manoeuvre (Manoeuvre): The Manoeuvre to assess

        Returns:
            Dict[str, float]: The sum of downgrades for each ManParm
        """
        return Results([mp.get_downgrades(manoeuvre.all_elements) for mp in self if not isinstance(mp.criteria, Combination)])
    
    def append_collectors(self, colls: Dict[str, Callable]):
        """Append each of a dict of collector methods to the relevant ManParm

        Args:
            colls (Dict[str, Callable]): dict of parmname: collector method
        """
        for mp, col in colls.items():
            self.data[mp].append(col)

    @staticmethod
    def create_defaults_f3a(**kwargs):
        mps = ManParms([
            ManParm("speed", inter_f3a_speed, 30.0),
            ManParm("loop_radius", inter_f3a_radius, 55.0),
            ManParm("line_length", inter_f3a_length, 130.0),
            ManParm("point_length", inter_f3a_length, 10.0),
            ManParm("continuous_roll_rate", inter_f3a_roll_rate, np.pi/2),
            ManParm("partial_roll_rate", inter_f3a_roll_rate, np.pi/2),
            ManParm("snap_rate", inter_f3a_roll_rate, 4*np.pi),
            ManParm("stallturn_rate", inter_f3a_roll_rate, 2*np.pi),
            ManParm("spin_rate", inter_f3a_roll_rate, 2*np.pi),
        ])
        for k,v in kwargs.items():
            if isinstance(v, Number):
                mps.data[k].default = v
            elif isinstance(v, ManParm):
                mps.data[k] = v
        return mps

    def update_defaults(self, intended: Manoeuvre):
        """Pull the parameters from a manoeuvre object and update the defaults of self based on the result of 
        the collectors.

        Args:
            intended (Manoeuvre): Usually a Manoeuvre that has been resized based on an alingned state
        """

        for mp in self:
            flown_parm = mp.collect(intended.all_elements)
            if len(flown_parm) >0:
                if isinstance(mp.criteria, Combination):
                    default = mp.criteria.check_option(flown_parm)
                else:
                    default = np.mean(flown_parm)
                mp.default = default
            
                

class MPValue:
    def __init__(self, value, minval, maxval, slope):
        self.value = value
        self.minval = minval
        self.maxval = maxval
        self.slope = slope



