from typing import Union
from flightanalysis.schedule.figure_rules import Categories
from .p_21 import p21
from .f_21 import f21
from .p_23 import p23
from .f_23 import f23


known_schedules = {
    Categories.F3A: dict(P21 = p21,F21 = f21, P23=p23, F23=f23),
    Categories.IMAC: dict()
}

def get_schedule(discipline: Union[str, Categories], name: str):
    if isinstance(discipline, str):
        discipline = Categories[discipline]
    return known_schedules[discipline][name]
    