import enum
from typing import List, Dict, Callable, Union
import numpy as np
import pandas as pd
from numbers import Number
from flightanalysis.base import Collection
from flightanalysis.schedule.manoeuvre import Manoeuvre
from flightanalysis.state import State
from flightanalysis.schedule.scoring import *
from numbers import Number
from . import Collector, Collectors, MathOpp, FunOpp, ItemOpp, Opp
from dataclasses import dataclass, field
from typing import Any
import numpy as np


@dataclass
class ManParm(Opp):
    """This class represents a parameter that can be used to characterise the geometry of a manoeuvre.
    For example, the loop diameters, line lengths, roll direction. 
        name (str): a short name, must work as an attribute so no spaces or funny characters
        criteria (Comparison): The comparison criteria function to be used when judging this parameter
        default (float): A default value (or default option if specified in criteria)
        collectors (Collectors): a list of functions that will pull values for this parameter from an Elements 
            collection. If the manoeuvre was flown correctly these should all be the same. The resulting list 
            can be passed through the criteria (Comparison callable) to calculate a downgrade.

    """
    criteria: Criteria
    default:Any=None
    collectors:Collectors=field(default_factory=lambda : Collectors())


    @property
    def n(self):
        return len(self.criteria.desired[0]) if isinstance(self.criteria, Combination) else None
        
    def to_dict(self):
        return dict(
            name = self.name,
            criteria = self.criteria.to_dict(),
            default = self.default,
            collectors = self.collectors.to_dict()
        )
    
    @staticmethod
    def from_dict(data: dict):
        return ManParm(
            name = data["name"],
            criteria = Criteria.from_dict(data["criteria"]),
            default = data["default"] if 'default' in data else data['defaul'], # because default is reserverd in javascript
            collectors = Collectors.from_dict(data["collectors"])
        )

    def append(self, collector: Union[Opp, Collector, Collectors]):
        if isinstance(collector, Opp) or isinstance(collector, Collector):
            self.collectors.add(collector)    
        elif isinstance(collector, Collectors):
            for coll in collector:
                self.append(coll)
        else:
            raise ValueError(f"expected a Collector or Collectors not {collector.__class__.__name__}")

    def assign(self, id, collector):
        self.collectors.data[id] = collector

    def collect(self, els):
        return {str(collector): collector(els) for collector in self.collectors}

    def collect_vis(self, els, state: State):
        return [np.mean([c.visibility(els, state) for c in colls.list_parms()]) for colls in self.collectors]

    def get_downgrades(self, els, state: State=None):
        coll = self.collect(els)
        vs = list(coll.values())
        meas = Measurement(
            vs,
            np.full(len(vs), self.default),
            np.full(len(vs), 0.4) if state is None else np.array(self.collect_vis(els, state))
        )

        keys, errors, dgs = self.criteria(list(coll.keys()), list(coll.values())) 
        return Result(self.name, meas, vs, errors, dgs * meas.visibility, keys)

    @property
    def value(self):
        if isinstance(self.criteria, Comparison):
            return self.default
        elif isinstance(self.criteria, Combination):
            return self.criteria[self.default]

    def valuefunc(self, id:int=0) -> Callable:
        """Create a function to return the value of this manparm from a manparms collection.
        
        Args:
            id (int, optional): The element id to return if reading the default from a Combination
            criteria. Defaults to 0.

        Raises:
            Exception: If some unknown criteria is being used

        Returns:
            Callable: function to get the default value for this manparm from the mps collection
        """
        if isinstance(self.criteria, Combination):
            return lambda mps: mps.data[self.name].value[id]
        else:
            return lambda mps: mps.data[self.name].value 
    

    def copy(self):
        return ManParm(name=self.name, criteria=self.criteria, default=self.default, collectors=self.collectors.copy())

    def list_parms(self):
        return [self]

    def __repr__(self):
        return f'ManParm({self.name}, {self.criteria.__class__.__name__}, {self.default})'

class ManParms(Collection):
    VType=ManParm
    uid="name"

    def collect(self, manoeuvre: Manoeuvre, state: State=None) -> Results:
        """Collect the comparison downgrades for each manparm for a given manoeuvre.

        Args:
            manoeuvre (Manoeuvre): The Manoeuvre to assess

        Returns:
            Dict[str, float]: The sum of downgrades for each ManParm
        """
        return Results("Inter",[mp.get_downgrades(manoeuvre.all_elements(), state) for mp in self if not isinstance(mp.criteria, Combination)])
    
    def append_collectors(self, colls: Dict[str, Callable]):
        """Append each of a dict of collector methods to the relevant ManParm

        Args:
            colls (Dict[str, Callable]): dict of parmname: collector method
        """
        for mp, col in colls.items():
            self.data[mp].append(col)

    def update_defaults(self, intended: Manoeuvre):
        """Pull the parameters from a manoeuvre object and update the defaults of self based on the result of 
        the collectors.

        Args:
            intended (Manoeuvre): Usually a Manoeuvre that has been resized based on an alinged state
        """

        for mp in self:
            flown_parm = list(mp.collect(intended.all_elements()).values())
            if len(flown_parm) > 0:
                if mp.default is not None:
                    if isinstance(mp.criteria, Combination):
                        default = mp.criteria.check_option(flown_parm)
                    else:
                        default = np.mean(np.abs(flown_parm)) * np.sign(mp.default)
                    mp.default = default

    def remove_unused(self):
        return ManParms([mp for mp in self if len(mp.collectors) > 0])

