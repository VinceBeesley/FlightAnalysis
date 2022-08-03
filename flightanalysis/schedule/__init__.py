"""This module models the aerobatic schedule and the rules that should be applied to it.

It is split into the definition in the ManDef, ManParm and ElDef classes and the 
implementation in the Schedule, Manoeuvre and El classes.

The definition provides a means to describe an aerobatic schedule and the rules that 
should apply to it. It is used to create template implementations and to link
implementations to the relevant cross element scoring criteria.

Criteria are devided into Inter Element and Intra Element. Intra element criteria consider
local changes that can be assessed within the element alone. Inter element criteria
consider the measurements that an element must meet in order to describe an 
aerobatic sequence.

Inter Element Criteria:
    loop element average radius, 
    line element length, 
    line element combined length,
    line element average roll rate,
    roll element amount performed,
    loop element amount performed,
    average speed, 

Intra Element Criteria:
    changes in loop radius
    changes in line angle
    loop barreling
    changes in roll rate
    changes in speed

Intra element criteria are handled by the element objects themselves. 

Inter element criteria are handled by the ManParm objects, which sit within the 
manoeuvre definition but take measurements of an implementation.

"""
from .elements import Loop, Line, Snap, Spin, StallTurn
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
    IMAC = dict(
        SPORTSMAN_2022 = "../data/IMACSportsman2022.json"
    )
)


import json
from typing import Union
def get_schedule(category: Union[str, Categories], name:str) -> Schedule:
    if isinstance(category, Categories): 
        category = category.name
    json_string = resource_stream(__name__, _jsons[category][name]).read().decode()
    return Schedule(**json.loads(json_string))