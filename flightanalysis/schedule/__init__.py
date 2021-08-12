from .element import rollmaker, reboundrollmaker, rollsnapcombomaker, LoopEl, LineEl, SnapEl, SpinEl, StallTurnEl
from .manoeuvre import Manoeuvre
from .schedule import Schedule


from .p_21 import p21
from .f_21 import f21
#from .p_23 import p23
#from .f_23 import f23


known_schedules = dict(
    F3A = dict(P21 = p21,F21 = f21),
    IMAC = dict()
)

def get_schedule(discipline: str, name: str):
    return known_schedules[discipline][name]