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
from numbers import Number


class MPO:
    def get_vf(self, arg):
        if isinstance(arg, str):
            return lambda mps: mps[self.a].value
        elif isinstance(arg, MPO):
            return lambda mps: arg(mps)
        elif isinstance(arg, Number):
            return lambda mps: arg
        elif isinstance(arg, ManParm):
            return lambda mps: arg.value    

    def __abs__(self):
        return MPfun(self, "abs")

    def __add__(self, other):
        return MPOpp(self, other, "+")

    def __radd__(self, other):
        return MPOpp(other, self, "+")

    def __mul__(self, other):
        return MPOpp(self, other, "*")

    def __rmul__(self, other):
        return MPOpp(other, self, "*")

    def __sub__(self, other):
        return MPOpp(self, other, "-")

    def __rsub__(self, other):
        return MPOpp(other, self, "-")

    def __div__(self, other):
        return MPOpp(self, other, "/")

    def __rdiv__(self, other):
        return MPOpp(other, self, "/")


class MPOpp(MPO):
    """This class facilitates various ManParm opperations and their serialisation"""
    opps = ["+", "-", "*", "/"]
    def __init__(self, a, b, opp:str):
        assert opp in MPOpp.opps
        self.a = a
        self.b = b
        self.opp = opp

    def __call__(self, mps):
        if self.opp == "+":
            return self.get_vf(self.a)(mps) + self.get_vf(self.b)(mps)
        elif self.opp == "-":
            return self.get_vf(self.a)(mps) - self.get_vf(self.b)(mps)
        elif self.opp == "*":
            return self.get_vf(self.a)(mps) * self.get_vf(self.b)(mps)
        elif self.opp == "/":
            return self.get_vf(self.a)(mps) / self.get_vf(self.b)(mps)

    def __str__(self):
        return f"({str(self.a)}{self.opp}{str(self.b)})"

    @staticmethod
    def parse(inp:str, mps):
        if inp[0] == "(" and inp[-1] == ")":
            bcount = 0
            for i, l in enumerate(inp):
                bcount += 1 if l=="(" else 0
                bcount -=1 if l==")" else 0
            
                if bcount == 1 and l in MPOpp.opps:
                    return MPOpp(
                        ManParm.parse(inp[1:i], mps),
                        ManParm.parse(inp[i+1:-1], mps),
                        l
                    )
                    
        raise ValueError(f"cannot read an MPOpp from the outside of {inp}")



class MPfun(MPO):
    """This class facilitates various functions that operate on ManParms and their serialisation"""
    funs = ["abs"]
    def __init__(self, a, opp: str):
        assert opp in MPfun.funs
        self.a = a
        self.opp = opp

    def __call__(self, mps):
        return {
            'abs': abs(self.get_vf(self.a)(mps))
        }[self.opp]
    
    def __str__(self):
        return f"{self.opp}({str(self.a)})"

    @staticmethod 
    def parse(inp: str, mps):
        for fun in MPfun.funs:
            if len(fun) >= len(inp) -2:
                continue
            if fun == inp[:len(fun)]:
                return MPfun(
                    ManParm.parse(inp[len(fun)+1:-1], mps), 
                    fun
                )
        raise ValueError(f"cannot read an MPfun from the outside of {inp}")
            

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
    
    def __add__(self, other):
        return MPOpp(self, other, "+")

    def __radd__(self, other):
        return MPOpp(other, self, "+")

    def __mul__(self, other):
        return MPOpp(self, other, "*")

    def __rmul__(self, other):
        return MPOpp(other, self, "*")

    def __sub__(self, other):
        return MPOpp(self, other, "-")

    def __rsub__(self, other):
        return MPOpp(other, self, "-")

    def __div__(self, other):
        return MPOpp(self, other, "/")

    def __rdiv__(self, other):
        return MPOpp(other, self, "/")

    def __str__(self):
        return self.name

    def __abs__(self):
        return MPfun(self, "abs")
    
    @staticmethod
    def parse(inp, mps):
        """Parse a manparm or a MPO from a string"""
        for test in [
            lambda inp, mps : MPfun.parse(inp, mps),
            lambda inp, mps : MPOpp.parse(inp, mps),
            lambda inp, mps : float(inp)
        ]: 
            try: 
                return test(inp.strip(" "), mps)
            except ValueError:
                pass
        else:
            return mps[inp]


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



