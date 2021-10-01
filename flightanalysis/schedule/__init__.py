from .element import rollmaker, reboundrollmaker, rollsnapcombomaker, LoopEl, LineEl, SnapEl, SpinEl, StallTurnEl
from .manoeuvre import Manoeuvre
from .schedule import Schedule

from .figure_rules import Categories, rules
from pkg_resources import resource_stream


_jsons = dict(
    F3A = dict(
        P21 = "../data/P21.json",
        F21 = "../data/F21.json",
        P23 = "../data/P23.json",
        F23 = "../data/F23.json",
    ), 
    IMAC = dict()
)


import json
from typing import Union
def get_schedule(category: Union[str, Categories], name:str):
    if isinstance(category, Categories): 
        category = category.name
    json_string = resource_stream(__name__, _jsons[category][name]).read().decode()
    return Schedule(**json.loads(json_string))