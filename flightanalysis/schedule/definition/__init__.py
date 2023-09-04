
from typing import Callable
from numbers import Number

from .operations import *
from .manoeuvre_info import ManInfo, BoxLocation, Orientation, Direction, Height, Position
from .collectors import Collector, Collectors

from .manoeuvre_parameters import ManParm, ManParms

def _a(arg):
    if isinstance(arg, ManParm):
        return arg.valuefunc()
    elif isinstance(arg, Number):
        return lambda mps: arg
    elif isinstance(arg, Opp):
        return arg
    

from .element_definition import ElDef, ElDefs
from .manoeuvre_definition import ManDef
from .sched_def import SchedDef, ScheduleInfo
from .manoeuvre_builder import ManoeuvreBuilder, f3amb, MBTags
