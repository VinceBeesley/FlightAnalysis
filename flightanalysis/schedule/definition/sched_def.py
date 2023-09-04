from . import ManDef, ManInfo, ManParms
from flightanalysis import State
from typing import Dict, Tuple, Union
from geometry import Transformation
from flightanalysis.schedule.schedule import Schedule
from flightanalysis.schedule.elements import Line
from flightanalysis.base.collection import Collection
from json import dump, load
from flightanalysis.base.numpy_encoder import NumpyEncoder
from dataclasses import dataclass
from flightanalysis.data import list_resources, get_json_resource

@dataclass
class ScheduleInfo:
    category: str
    name: str

    @staticmethod
    def from_str(fname):
        if fname.endswith("_schedule.json"):
            fname = fname[:-14]
        info = fname.split("_")
        if len(info) == 1:
            return ScheduleInfo("f3a", info[0].lower())
        else:
            return ScheduleInfo(info[0].lower(), info[1].lower())

    def __str__(self):
        name = self.name if self.category == "f3a" else f"{self.category}_{self.name}"
        return name.lower()

    def definition(self):
        return SchedDef.load(self)

    @staticmethod
    def from_fcj_sch(fcj):
        return ScheduleInfo(fcj[0].lower(), fcj[1].lower())

    @staticmethod
    def build(category, name):
        return ScheduleInfo(category.lower(), name.lower())


schedule_library = [ScheduleInfo.from_str(fname) for fname in list_resources('schedule')]


class SchedDef(Collection):
    VType=ManDef
    def add_new_manoeuvre(self, info: ManInfo, defaults=None):
        return self.add(ManDef(info,defaults))

    def create_schedule(self, depth: float, wind: float) -> Schedule:
        return Schedule(
            {m.uid: m.create(m.info.initial_transform(depth, wind)) for m in self}
        )      

    def create_template(self,depth:float=170, wind:int=-1) -> Tuple[Schedule, State]:
        templates = []
        ipos = self[0].info.initial_position(depth,wind)
        
        mans = []
        for md in self:

            itrans=Transformation(
                ipos if len(templates) == 0 else templates[-1][-1].pos,
                md.info.start.initial_rotation(wind)
            )
            man = md.create(itrans)
            templates.append(man.create_template(itrans))
            mans.append(man)
        return Schedule(mans), State.stack(templates)

    def create_el_matched_template(self, intended: Schedule):
        for md, man in zip(self, intended):
            if isinstance(man, Line):
                pass

    def update_defaults(self, sched: Schedule):
        # TODO need to consider the entry line
        for md, man in zip(self, sched):
            md.mps.update_defaults(man)

    def to_json(self, file: str) -> str:
        with open(file, "w") as f:
            dump(self.to_dict(), f, cls=NumpyEncoder, indent=2)
        return file

    @staticmethod
    def from_json(file:str):
        with open(file, "r") as f:
            return SchedDef.from_dict(load(f))
        
    @staticmethod
    def load(name: Union[str,ScheduleInfo]):
        if isinstance(name, ScheduleInfo):
            name = str(name)
        return SchedDef.from_dict(get_json_resource(f"{name.lower()}_schedule"))
    