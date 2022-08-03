
from typing import Callable
from numbers import Number


from .manparms import ManParm, ManParms

def _a(arg):
    if isinstance(arg, Callable): 
        return arg
    elif isinstance(arg, ManParm):
        return arg.valuefunc()

from .eldefs import ElDef, ElDefs

from .mandef import ManDef
