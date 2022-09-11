from telnetlib import DO
import numpy as np
import pandas as pd
from flightanalysis.state import State
from geometry import Transformation, PZ, Point, angle_diff
from json import load
from flightanalysis.criteria import *
from flightanalysis.base.collection import Collection


class DownGrade:
    def __init__(self, name, measurement, criteria):
        self.name = name
        self.measurement = measurement
        self.criteria = criteria

    def measure(self, el, flown, template):
        return getattr(el, self.measurement)(flown, template)
    
    def apply(self, el, flown, template):
        return self.criteria(self.name, self.measure(el, flown, template))


class DownGrades(Collection):
    VType = DownGrade
    uid = "name"

    def measuredf(self, el, fl, tp):
        intra_measurements = {es.name: es.measure(el, fl, tp) for es in el.intra_scoring }

        return pd.DataFrame(
            np.array(list(intra_measurements.values())).T, 
            columns=list(intra_measurements.keys()),
            index = el.measure_length(fl, tp)
        )
    
    def dgs(self, mdf: pd.DataFrame):
        return Results([es.criteria(es.name, mdf[es.name]) for es in self])


class El:   
    parameters = ["speed"]
    intra_scoring = DownGrades([])
    exit_scoring = DownGrades([])

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
        """Change the reference coordinate frame for a flown element to the
        elements coord"""   
        return flown.move_back(Transformation.from_coord(self.coord(template)))

    def measure_end_roll_angle(self, flown: State, template:State):
        return np.array([self.measure_roll_angle(flown, template)[-1]])

    def measure_ip_track(self, flown: State, template:State):
        vels = flown.att.transform_point(flown.vel) 
        return np.arcsin(vels.z/abs(vels) ) 

    def measure_op_track(self, flown: State, template:State):
        vels = flown.att.transform_point(flown.vel) 
        return np.arcsin(vels.y/abs(vels) ) 

    def measure_roll_rate(self, flown: State, template:State):
        return flown.p 

    def measure_roll_angle(self, flown: State, template:State):
        """The roll angle given a state in the loop coordinate frame"""
        roll_vector = flown.att.inverse().transform_point(PZ(1))
        return np.unwrap(np.arctan2(roll_vector.z, roll_vector.y))

    def measure_eq_tp_roll_angle(self, flown, template):
        tp_angles = self.measure_roll_angle(template, template)
        
        return self.measure_ratio(flown, template) * (tp_angles[-1] - tp_angles[0]) + tp_angles[0]

    def measure_length(self, flown: State, template:State):
        return np.cumsum(abs(flown.vel) * flown.dt)

    def measure_ratio(self, flown: State, template:State):
        return flown.x / flown.x[-1]

    def measure_roll_angle_error(self, flown: State, template:State):
        fl_angles = self.measure_roll_angle(flown, template) 
        tp_angles = self.measure_eq_tp_roll_angle(flown, template)
        return angle_diff(fl_angles, tp_angles)
        

    def measure_speed(self, flown, template):
        return abs(flown.vel)

    def score_series_builder(self, index):
        return lambda data: pd.Series(data, index=index)

    def intra_score(self, flown: State, template:State, previous: Result=None) -> Results:
        """The previous argument allows the scoring to pick up carry over (less than 0.5 mark errors) 
        from the last element if there was one"""
        mdf = self.intra_scoring.measuredf(self, flown, template)
        return self.intra_scoring.dgs(mdf)

    def analyse(self, flown:State, template:State, previous: Result=None) -> Results:
        fl =  self.setup_analysis_state(flown, template)
        tp =  self.setup_analysis_state(template, template)
        return self.intra_score(fl, tp)


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

def from_json(file):
    with open(file, "r") as f:
        return El.from_dict(load(f))

El.from_json = from_json

from flightanalysis.base.collection import Collection


class Elements(Collection):
    VType=El
    def get_parameter_from_element(self, element_name: str, parameter_name: str):
        return getattr(self.data[element_name], parameter_name)  
    
    @staticmethod
    def from_dicts(data):
        return Elements([El.from_dict(d) for d in data])


class ElResults(El):
    def __init__(self, el: El, results:Results):
        self.el = el
        self.results = results
    
    @property
    def uid(self):
        return self.el.uid

    

class ElementsResults(Collection):
    VType=ElResults

    def downgrade(self):
        return sum(er.results.downgrade() for er in self)
    
    def downgrade_list(self):
        return [er.results.downgrade() for er in self]
    


    