import enum
from typing import List, Callable, Union, Dict
import numpy as np
from flightanalysis.schedule.elements import *
from inspect import getfullargspec
from functools import partial
from . import ManParm, ManParms, _a, Opp, ItemOpp
from flightanalysis.base.collection import Collection
from numbers import Number
from . import Collector, Collectors
import inspect


class ElDef:
    """This class creates a function to build an element (Loop, Line, Snap, Spin, Stallturn)
    based on a ManParms collection. 

    The eldef also contains a set of collectors. These are a dict of str:callable pairs
    that collect the relevant parameter for this element from an Elements collection.
    """
    def __init__(self, name, Kind, props: Dict[str, Union[Number, Opp]]):
        """ElDef Constructor

        Args:
            name (_type_): the name of the Eldef, must be unique and work as an attribute
            Kind (_type_): the class of the element (Loop, Line etc)
            props (dict): The element property generators (Number, Opp)
        """
        self.name = name
        self.Kind = Kind
        self.props = props       
        self.collectors = Collectors.from_eldef(self)

    def get_collector(self, name):
        return self.collectors[f"{self.name}.{name}"]

    def to_dict(self):
        return dict(
            name = self.name,
            Kind = self.Kind.__name__,
            props = {k: str(v) for k, v in self.props.items()}
        )

    @staticmethod
    def from_dict(data: dict, mps: ManParms): 
        return ElDef(
            name=data["name"],
            Kind = El.from_name(data["Kind"]),
            props = {k: ManParm.parse(v, mps) for k, v in data["props"].items()}
        )

    def __call__(self, mps: ManParms) -> El:
        kwargs = {}
        args = getfullargspec(self.Kind.__init__).args
        for pname, prop in self.props.items():
            # only use the parameter if it is actually needed to create the element
            if pname in args: 
                kwargs[pname] = _a(prop)(mps)

        return self.Kind(uid=self.name, **kwargs) 
    
    def build(Kind, name, *args, **kwargs):
        #if *args are passed, tag them onto kwargs
        elargs = list(inspect.signature(Kind.__init__).parameters)[1:-1]
        for arg, argname in zip(args, elargs[:len(args)] ):
            kwargs[argname] = arg
        
        ed = ElDef(name, Kind, kwargs)
        
        for key, value in kwargs.items():
            if isinstance(value, ManParm):
                value.append(ed.get_collector(key))
            elif isinstance(value, ItemOpp):
                value.a.assign(value.item, ed.get_collector(key))
        
        return ed

    def rename(self, new_name):
        return ElDef(new_name, self.Kind, self.pfuncs)
    
    @property
    def id(self):
        return int(self.name.split("_")[1])

class ElDefs(Collection):
    VType=ElDef
    uid="name"
    """This class wraps a dict of ElDefs, which would generally be used sequentially to build a manoeuvre.
    It provides attribute access to the ElDefs based on their names. 
    """

    @staticmethod
    def from_dict(data: dict, mps: ManParms):
        return ElDefs([ElDef.from_dict(v, mps) for v in data.values()])

    def to_dict(self):
        return {v.name: v.to_dict() for v in self}
    
    def get_new_name(self): 
        new_id = 0 if len(self.data) == 0 else list(self.data.values())[-1].id + 1
        return f"e_{new_id}"

    def add(self, ed: Union[ElDef, List[ElDef]]) -> Union[ElDef, List[ElDef]]:
        """Add a new element definition to the collection. Returns the ElDef

        Args:
            ed (Union[ElDef, List[ElDef]]): The ElDef or list of ElDefs to add

        Returns:
            Union[ElDef, List[ElDef]]: The ElDef or list of ElDefs added
        """
        if isinstance(ed, ElDef):
            self.data[ed.name] = ed
            return ed
        else:
            return [self.add(e) for e in ed]


    def builder_list(self, name:str) ->List[Callable]:
        """A list of the functions that return the requested parameter when constructing the elements from the mps"""
        return [e.props[name] for e in self if name in e.props]

    def builder_sum(self, name:str) -> Callable:
        """A function to return the sum of the requested parameter used when constructing the elements from the mps"""
        return sum(self.builder_list(name))

    def collector_list(self, name: str) -> Collectors:
        """A list of the functions that return the requested parameter from an elements collection"""
        return Collectors([e.get_collector(name) for e in self if f"{e.name}.{name}" in e.collectors.data])


    def collector_sum(self, name) -> Callable:
        """A function that returns the sum of the requested parameter from an elements collection"""
        return sum(self.collector_list(name))
    
