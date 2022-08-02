
from typing import Callable
from numbers import Number


from .manparms import ManParm, ManParms

def _a(arg):
    if isinstance(arg, Callable): 
        return arg
    elif isinstance(arg, Number):
        return lambda mps: arg
    elif isinstance(arg, str): 
        return lambda mps: mps[arg].value

from .eldefs import ElDef, ElDefs

from .mandef import ManDef
