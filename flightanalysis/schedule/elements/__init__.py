from flightanalysis.state import State
from typing import Dict

class El:   
    parameters = ["speed"]

    def __init__(self, uid: str, speed: float):        
        self.uid = uid
        self.speed = speed

    def get_data(self, sec: State):
        return State(sec.data.loc[sec.data.element == self.uid])

    def _add_rolls(self, el: State, roll: float) -> State:
        if not roll == 0:
            el = el.superimpose_roll(roll)
        return el.label(element=self.uid)

    def __eq__(self, other):
        if not self.__class__ == other.__class__:
            return False
        if not self.uid == other.uid:
            return False
        return np.all([getattr(parm, self) == other.getattr(parm, other) for parm in self.__class__.parameters])

    def to_dict(self):
        return dict(type=self.__class__.__name__, **self.__dict__)

    def set_parms(self, **parms):
        new_inst = self.__class__(**self.__dict__)
        for key, value in parms.items():
            setattr(new_inst, key, value)
        return new_inst


from .line import Line
from .loop import Loop
from .snap import Snap
from .spin import Spin
from .stall_turn import StallTurn

els = {c.__name__.lower(): c for c in El.__subclasses__()}

El.from_name = lambda name: els[name.lower()]

from .constructors import *

class Elements:
    def __init__(self, els: Dict[str, El]):
        self.els=els

    def __getattr__(self, name):
        return self.els[name]

    def __iter__(self):
        for el in self.els.values():
            yield el
    
    def __getitem__(self, value):
        return list(self.els.values())[value]

    def to_list(self):
        return list(self.els.values())

    @staticmethod
    def from_list(els):
        return Elements({el.uid: el for el in els})

    def get_parameter_from_element(self, element_name: str, parameter_name: str):
        return getattr(self.els[element_name], parameter_name)