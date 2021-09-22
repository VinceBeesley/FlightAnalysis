
from .p_21 import p21
from .f_21 import f21
from .p_23 import p23
from .f_23 import f23


known_schedules = dict(
    F3A = dict(P21 = p21,F21 = f21, P23=p23, F23=f23),
    IMAC = dict()
)

def get_schedule(discipline: str, name: str):
    return known_schedules[discipline][name]