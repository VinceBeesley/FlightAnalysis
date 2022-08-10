
from typing import Callable
from numbers import Number

from .manoeuvre_info import ManInfo, BoxLocation, Orientation, Direction, Height, Position
from .manoeuvre_parameters import ManParm, ManParms, MPValue

def _a(arg):
    if isinstance(arg, Callable): 
        return arg
    elif isinstance(arg, ManParm):
        return arg.valuefunc()
    elif isinstance(arg, Number):
        return lambda mps: arg

from .element_definition import ElDef, ElDefs

from .manoeuvre_definition import ManDef


from .schedule_definition import SchedDef

