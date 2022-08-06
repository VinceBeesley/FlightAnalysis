
from typing import Callable
from numbers import Number

from .maninfo import ManInfo, BoxLocation, Orientation, Direction, Height, Position
from .manparms import ManParm, ManParms, MPValue

def _a(arg):
    if isinstance(arg, Callable): 
        return arg
    elif isinstance(arg, ManParm):
        return arg.valuefunc()
    elif isinstance(arg, Number):
        return lambda mps: arg

from .eldefs import ElDef, ElDefs

from .mandef import ManDef


from .schedule_definition import SchedDef

