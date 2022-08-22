import numpy as np
from flightanalysis.state import State
from geometry import Transformation


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

    def setup_analysis_state(self, flown: State, template:State):
        """Change the reference coordinate frame for a flown loop element to the
        loop coord"""   
        return flown.move_back(Transformation.from_coord(self.coord(template)))




from .line import Line
from .loop import Loop
from .snap import Snap
from .spin import Spin
from .stall_turn import StallTurn

els = {c.__name__: c for c in El.__subclasses__()}

El.from_name = lambda name: els[name.lower()]

def from_dict(data):
    kind = data.pop("kind")
    return els[kind](**data)

El.from_dict = staticmethod(from_dict)


from flightanalysis.base.collection import Collection


class Elements(Collection):
    VType=El
    def get_parameter_from_element(self, element_name: str, parameter_name: str):
        return getattr(self.data[element_name], parameter_name)  
    
    @staticmethod
    def from_dicts(data):
        return Elements([El.from_dict(d) for d in data])


