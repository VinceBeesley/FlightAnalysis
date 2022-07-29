from flightanalysis.state import State
from typing import Dict

class El:   
    parameters = ["speed"]
    register = set()

    def __init__(self, uid: str, speed: float):        

        self.uid = El.make_id() if uid is None else uid

        if self.uid in El.register:
            raise Exception("attempting to create a new El with an existing key")
        El.register.add(self.uid)
        self.speed = speed

    @staticmethod
    def make_id():
        i=1
        while f"auto_{i}" in El.register:
            i+=1
        else:
            return f"auto_{i}"

    def get_data(self, sec: State):
        return State(sec.data.loc[sec.data.element == self.uid])

    def _add_rolls(self, el: State, roll: float) -> State:
        if not roll == 0:
            el = el.superimpose_roll(roll)
        return el.label(element=self.uid)

    def __eq__(self, other):
        return self.uid == other.uid

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

    @staticmethod
    def from_list(els):
        return Elements({el.uid: el for el in els})

