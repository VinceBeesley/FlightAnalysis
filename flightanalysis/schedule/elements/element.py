from __future__ import annotations
import numpy as np
import pandas as pd
from flightanalysis import State, Collection, Time
from flightanalysis.schedule.scoring import *
from geometry import Transformation, PX, PY, PZ, Point, angle_diff, Coord, Quaternion
from json import load, dumps


class Element:   
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

    def score_series_builder(self, index):
        return lambda data: pd.Series(data, index=index)

    def analyse(self, flown:State, template:State) -> Results:
#        fl =  self.setup_analysis_state(flown, template)
#        tp =  self.setup_analysis_state(template, template)
        return self.intra_scoring.apply(self, flown, template, self.ref_frame(template))

    def analyse_exit(self, fl, tp) -> Results:
        #fl =  self.setup_analysis_state(flown, template)
        #tp =  self.setup_analysis_state(template, template)
        return self.exit_scoring.apply(self, fl, tp, self.ref_frame(tp))

    def ref_frame(self, template: State) -> Transformation:
        return template[0].transform

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
    def intra_scoring(self) -> DownGrades:
        return DownGrades()

    @property
    def exit_scoring(self):
        return DownGrades([
            DownGrade(Measurement.track_y, f3a.single_track),
            DownGrade(Measurement.track_z, f3a.single_track),
            DownGrade(Measurement.roll_angle, f3a.single_roll),
        ])

    @classmethod
    def from_name(Cls, name) -> Element:
        for Child in Cls.__subclasses__():
            if Child.__name__.lower() == name.lower():
                return Child

    @classmethod
    def from_dict(Cls, data: dict):
        data=data.copy()
        return Element.from_name(data.pop("kind").lower())(**data)
    
    @classmethod
    def from_json(Cls, file):
        with open(file, "r") as f:
            return Element.from_dict(load(f))

    def length_vec(self, flown:State) -> Point:
        return flown.pos[-1] - flown.pos[0]
    
    def roll_vec(self, flown: State) -> Point:
        return flown.att[-1].transform_point(PX(
            np.sign(np.mean(flown.p)) * abs(self.roll)
        ))

    def speed_vec(self, flown: State) -> Point:
        return flown.att[-1].transform_point(flown.vel.mean())

    def rate_vec(self, flown: State) -> Point:
        flown.att[-1].transform_point(np.mean(flown.p))


class Elements(Collection):
    VType=Element
    def get_parameter_from_element(self, element_name: str, parameter_name: str):
        return getattr(self.data[element_name], parameter_name)  
    
    @staticmethod
    def from_dicts(data):
        return Elements([Element.from_dict(d) for d in data])
            