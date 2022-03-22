from flightanalysis.state import State


class El:
    _counter = 0

    @staticmethod
    def reset_counter():
        El._counter = 0

    def __init__(self, uid: int = None):
        if not uid:
            El._counter += 1
            self.uid = El._counter  # str(uuid4())
        else:
            self.uid = uid

    def get_data(self, sec: State):
        return State(sec.data.loc[sec.data.element == self.uid])

    def _add_rolls(self, el: State, rolls: float) -> State:
        if not rolls == 0:
            el = el.superimpose_roll(rolls)
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

from .constructors import *
