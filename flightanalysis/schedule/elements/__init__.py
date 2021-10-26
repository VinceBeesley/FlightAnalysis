from flightanalysis import Section


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

    def get_data(self, sec: Section):
        return Section(sec.data.loc[sec.data.element == self.uid])

    def _add_rolls(self, el: Section, rolls: float) -> Section:
        if not rolls == 0:
            el = el.superimpose_roll(rolls)
        el.data["element"] = self.uid
        return el

    def __eq__(self, other):
        return self.uid == other.uid

    def to_dict(self):
        return dict(type=self.__class__.__name__, **self.__dict__)


from .line import Line
from .loop import Loop
from .snap import Snap
from .spin import Spin
from .stall_turn import StallTurn

from .constructors import *
