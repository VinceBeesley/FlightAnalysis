from __future__ import annotations
import numpy as np
import pandas as pd
from flightanalysis import State, Collection, Time
from flightanalysis.schedule.scoring import *
from geometry import Transformation, PX, PY, PZ, Point, angle_diff, Coord, Quaternion
from json import load, dumps


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

    def score_series_builder(self, index):
        return lambda data: pd.Series(data, index=index)

    def analyse(self, flown:State, template:State) -> Results:
#        fl =  self.setup_analysis_state(flown, template)
#        tp =  self.setup_analysis_state(template, template)
        return self.intra_scoring.apply(self, flown, template, self.coord(template))

    def analyse_exit(self, fl, tp) -> Results:
        #fl =  self.setup_analysis_state(flown, template)
        #tp =  self.setup_analysis_state(template, template)
        return self.exit_scoring.apply(self, fl, tp, self.coord(tp))

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
    def intra_scoring(self) -> DownGrades:
        return DownGrades()

    @property
    def exit_scoring(self):
        return DownGrades([
            DownGrade(Measurement.track, f3a.single_track),
            DownGrade(Measurement.roll_angle, f3a.single_roll),
        ])

    @classmethod
    def from_name(Cls, name) -> El:
        for Child in Cls.__subclasses__():
            if Child.__name__.lower() == name.lower():
                return Child

    @classmethod
    def from_dict(Cls, data):        
        return El.from_name(data.pop("kind").lower())(**data)
    
    @classmethod
    def from_json(Cls, file):
        with open(file, "r") as f:
            return El.from_dict(load(f))



class Elements(Collection):
    VType=El
    def get_parameter_from_element(self, element_name: str, parameter_name: str):
        return getattr(self.data[element_name], parameter_name)  
    
    @staticmethod
    def from_dicts(data):
        return Elements([El.from_dict(d) for d in data])
            

class ElResults():
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
    
    def downgrade_df(self):
        df = pd.concat([idg.results.downgrade_df().sum() for idg in self], axis=1).T
        df["Total"] = df.T.sum()
        df["Element"] = [el.uid for el in self]
        return df.set_index("Element")


from .line import Line
from .loop import Loop
from .stall_turn import StallTurn
from .nose_drop import NoseDrop
from .pitch_break import PitchBreak
from .recovery import Recovery
from .autorotation import Autorotation


    