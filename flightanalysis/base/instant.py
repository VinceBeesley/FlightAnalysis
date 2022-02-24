
import numpy as np
from flightanalysis.base.constructs import Constructs
from abc import ABC, abstractmethod



class Instant(ABC):
    """Describes the the state of the aircraft
    """
    def __init__(self, data:dict):
        self.data = data

    @property
    def cols(self):
        return self.__class__._cols

    @property
    def _Period(self):
        return self.__class__.Period

    @property
    @abstractmethod
    def _cols(self) -> Constructs:
        pass

    def __getattr__(self, name):
        if name in self.data.keys():
            return self.data[name]
        elif name in self._cols.data.keys():
            return self._cols.data[name].fromdict(self.data)
        elif name in self._cols.gdata.keys():
            return self._cols.data[name].fromdict(self.data)
        
   # def copy(self, *args,**kwargs):
   #     # add the args to the kwargs
   #     kwargs = dict(kwargs, **{list(self.constructs.constructs.keys())[i]: arg for i, arg in enumerate(args)})
#
   #     old_constructs = {key: self.__getattr__(key) for key in self.existing_constructs() if not key in kwargs}
   #     
   #     new_constructs = {key: value for key, value in list(kwargs.items()) + list(old_constructs.items())}
#
   #     return Instant.from_constructs(**new_constructs)
        
