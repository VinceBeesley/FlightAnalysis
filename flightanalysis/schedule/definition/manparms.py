import enum
from typing import List, Dict, Callable, Union
import numpy as np
import pandas as pd
from numbers import Number
from flightanalysis.schedule.elements import Loop, Line, Snap, Spin, StallTurn, El, Elements
from flightanalysis.schedule.manoeuvre import Manoeuvre
from flightanalysis.criteria.comparison import *
from flightanalysis.criteria.local import Combination, AngleCrit

from functools import partial


class ManParm:
    """This class represents a parameter that can be used to characterise the geometry of a manoeuvre.
    For example, the loop diameters, line lengths, roll direction. 
    """
    def __init__(self, name:str, criteria: Union[Comparison, Combination], default=None, collectors: List[Callable]=None):
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
        return [collector(els) for collector in self.collectors]

    def get_downgrades(self, els):
        return self.criteria(*self.collect(els))

    @property
    def value(self):
        if isinstance(self.criteria, Comparison) or isinstance(self.criteria, AngleCrit):
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
        if isinstance(self.criteria, Comparison) or isinstance(self.criteria, AngleCrit):
            return lambda mps: mps.parms[self.name].value 
        elif isinstance(self.criteria, Combination):
            return lambda mps: mps.parms[self.name].value[id] 
            #return partial(
            #   lambda mps, i: mps.parms[self.name].value[i], 
            #   i=id
            # )
        else:
            raise Exception("Cant create a valuefunc in this case")
        

class ManParms:
    """This class wraps around a dict of ManParm. it provides attribute access to items based on their
    names and a constructer from a list of them (as the names are internal)
    """
    def __init__(self, parms:Dict[str, ManParm]={}):
        self.parms = parms
    
    def __getattr__(self, name):
        return self.parms[name]

    @staticmethod
    def from_list(mps: List[ManParm]):
        return ManParms({mp.name: mp for mp in mps})

    def add(self, parm):
        self.parms[parm.name] = parm
        return parm

    def collect(self, manoeuvre: Manoeuvre) -> Dict[str, float]:
        """Collect the comparison downgrades for each manparm for a given manoeuvre.

        Args:
            manoeuvre (Manoeuvre): The Manoeuvre to assess

        Returns:
            Dict[str, float]: The sum of downgrades for each ManParm
        """
        return {key: mp.get_downgrades(manoeuvre.elements) for key, mp in self.parms.items() if not isinstance(mp.criteria, Combination)}
    
    def append_collectors(self, colls: Dict[str, Callable]):
        """Append each of a dict of collector methods to the relevant ManParm

        Args:
            colls (Dict[str, Callable]): dict of parmname: collector method
        """
        for mp, col in colls.items():
            self.parms[mp].append(col)

    @staticmethod
    def create_defaults_f3a(**kwargs):
        mps = ManParms.from_list([
            ManParm("speed", f3a_speed, 30.0),
            ManParm("loop_radius", f3a_radius, 55.0),
            ManParm("line_length", f3a_length, 130.0),
            ManParm("point_length", f3a_length, 10.0),
            ManParm("continuous_roll_rate", f3a_roll_rate, np.pi),
            ManParm("partial_roll_rate", f3a_roll_rate, np.pi),
            ManParm("snap_rate", f3a_roll_rate, 4*np.pi),
            ManParm("stallturn_rate", f3a_roll_rate, 2*np.pi),
            ManParm("spin_rate", f3a_roll_rate, 2*np.pi),
        ])

        for k, v in kwargs.items():
            if isinstance(v, ManParm):
                mps.parms[v.name] = v
            elif isinstance(v, Number):
                mps.parms[k].default = v
        return mps

    def next_free_name(self, prefix: str):
        i=0
        while f"{prefix}{i}" in self.parms:
            i+=1
        else:
            return f"{prefix}{i}"


class MPValue:
    def __init__(self, value, minval, maxval, slope):
        self.value = value
        self.minval = minval
        self.maxval = maxval
        self.slope = slope



