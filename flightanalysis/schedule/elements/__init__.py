import numpy as np
import pandas as pd
from flightanalysis.state import State
from geometry import Transformation, PX, PY, PZ, Point, angle_diff, Coord
from json import load, dumps
from flightanalysis.criteria import *
from flightanalysis.base.collection import Collection
from flightanalysis.base.table import Time
from typing import Union

class DownGrade:
    def __init__(self, name, measurement, criteria):
        self.name = name
        self.measurement = measurement
        self.criteria = criteria

    def measure(self, el, flown, template):
        return self.criteria.preprocess(getattr(el, self.measurement)(flown, template))
    
    def apply(self, el, flown, template):
        return self.criteria(self.name, self.measure(el, flown, template), False)


class DownGrades(Collection):
    VType = DownGrade
    uid = "name"

    def apply(self, el, fl, tp):
        return Results([es.criteria(es.name, es.measure(el, fl, tp), False) for es in self])
       

class El:   
    parameters = ["speed"]

    def __init__(self, uid: str, speed: float):        
        self.uid = uid
        if speed < 0:
            raise ValueError("negative speeds are not allowed")
        self.speed = speed

    def get_data(self, st: State):
        return st.get_element(self.uid)

    def _add_rolls(self, el: State, roll: float) -> State:
        if not roll == 0:
            el = el.superimpose_rotation(PX(), roll)
        return el.label(element=self.uid)

    def __eq__(self, other):
        if not self.__class__ == other.__class__:
            return False
        if not self.uid == other.uid:
            return False
        return np.all([np.isclose(getattr(self, p), getattr(other, p), 0.01) for p in self.__class__.parameters])

    def __repr__(self):
        return dumps(self.to_dict(), indent=2)

    def to_dict(self):
        return dict(kind=self.__class__.__name__, **self.__dict__)

    def set_parms(self, **parms):
        kwargs = {k:v for k, v in self.__dict__.items() if not k[0] == "_"}

        for key, value in parms.items():
            if key in kwargs:
                kwargs[key] = value
        
        return self.__class__(**kwargs)


    def setup_analysis_state(self, flown: State, template:State):
        """Change the reference coordinate frame for a flown element to the
        elements coord"""   
        return flown.move_back(Transformation.from_coord(self.coord(template)))

    def measure_end_roll_angle(self, flown: State, template:State):
        return np.array([self.measure_roll_angle(flown, template)[-1]])

    def measure_ip_track(self, flown: State, template:State):
        vels = flown.att.transform_point(flown.vel) 
        return np.arcsin(vels.z/abs(vels) ) 

    def measure_end_ip_track(self, flown, template):
        return np.array([self.measure_ip_track(flown, template)[-1]])

    def measure_op_track(self, flown: State, template:State):
        vels = flown.att.transform_point(flown.vel) 
        return np.arcsin(vels.y/abs(vels) ) 

    def measure_end_op_track(self, flown, template):
        return np.array([self.measure_op_track(flown, template)[-1]])

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

    def analyse(self, flown:State, template:State) -> Results:
        fl =  self.setup_analysis_state(flown, template)
        tp =  self.setup_analysis_state(template, template)
        return self.intra_scoring.apply(self, fl, tp)

    def analyse_exit(self, flown, template) -> Results:
        fl =  self.setup_analysis_state(flown, template)
        tp =  self.setup_analysis_state(template, template)
        return self.exit_scoring.apply(self, fl, tp)

    def coord(self, template: State) -> Coord:
        """Create the coordinate frame. 
        Origin on start point, X axis in velocity vector
        if the x_vector is in the xz plane then the z vector is world y,
        #otherwise the Z vector is world X
        """
        x_vector = template[0].att.transform_point(PX(1))
        z_vector = PY(1.0) if abs(x_vector.y[0]) < 0.1 else PX(1.0)
        return Coord.from_zx(template[0].pos, z_vector, x_vector)

    @staticmethod
    def create_time(duration: float, time: Time=None):
        if time is None:
            n = int(np.ceil(duration * State._construct_freq))
            return Time.from_t(
                np.linspace(0, duration, n if n > 1 else n+1))
        else:
            #probably want to extend by one timestep
            return time.reset_zero().scale(duration)

    @property
    def exit_scoring(self):
        return DownGrades([
            DownGrade("ip_track", "measure_end_ip_track", basic_angle_f3a),
            DownGrade("op_track", "measure_end_op_track", basic_angle_f3a),
            DownGrade("roll_angle", "measure_end_roll_angle", basic_angle_f3a),
        ])


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
    

from .line import Line
from .loop import Loop
from .stall_turn import StallTurn
from .nose_drop import NoseDrop
from .pitch_break import PitchBreak
from .recovery import Recovery
from .autorotation import Autorotation

els = {c.__name__.lower(): c for c in El.__subclasses__()}

El.from_name = lambda name: els[name.lower()]

def from_dict(data):
    kind = data.pop("kind").lower()
    return els[kind](**data)

El.from_dict = staticmethod(from_dict)

def from_json(file):
    with open(file, "r") as f:
        return El.from_dict(load(f))

El.from_json = from_json


    