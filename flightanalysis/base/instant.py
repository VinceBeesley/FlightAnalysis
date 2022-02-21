
import numpy as np
from flightanalysis.base.constructs import Constructs


class Instant():
    """Describes the the state of the aircraft
    """
    def __init__(self, constructs: Constructs, data:dict):
        #assert_vars(data.keys())
        self.constructs = constructs
        self.data = data

        consts = self.existing_constructs()
        assert np.all([var in consts for var in ["pos", "att"]])

    def __getattr__(self, name):
        if name in self.data.keys():
            return self.data[name]
        elif name in self.constructs.keys():
            return self.constructs[name].fromdict(self.data)


    def existing_constructs(self):
        return self.constructs.existing_constructs(self.data.keys())

    def copy(self, *args,**kwargs):
        # add the args to the kwargs
        kwargs = dict(kwargs, **{list(self.constructs.constructs.keys())[i]: arg for i, arg in enumerate(args)})

        old_constructs = {key: self.__getattr__(key) for key in self.existing_constructs() if not key in kwargs}
        
        new_constructs = {key: value for key, value in list(kwargs.items()) + list(old_constructs.items())}

        return Instant.from_constructs(**new_constructs)
        
