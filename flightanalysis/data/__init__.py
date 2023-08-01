from pathlib import Path

from flightanalysis.schedule import SchedDef
from pkg_resources import resource_stream, resource_listdir
from json import loads
from dataclasses import dataclass


def get_schedule_definition(name):
    if isinstance(name, ScheduleInfo):
        name = str(name)
    data = resource_stream(__name__, f"{name.lower()}.json").read().decode()
    return SchedDef.from_dict(loads(data))


@dataclass
class ScheduleInfo:
    category: str
    name: str

    @staticmethod
    def from_str(fname):
        if fname.endswith(".json"):
            fname = fname.split(".")[0]
        info = fname.split("_")
        if len(info) == 1:
            return ScheduleInfo("f3a", info[0].lower())
        else:
            return ScheduleInfo(info[0].lower(), info[1].lower())

    def __str__(self):
        name = self.name if self.category == "f3a" else f"{self.category}_{self.name}"
        return name.lower()

    def definition(self):
        return get_schedule_definition(str(self))

    @staticmethod
    def from_fcj_sch(fcj):
        return ScheduleInfo(fcj[0].lower(), fcj[1].lower())

    @staticmethod
    def build(category, name):
        return ScheduleInfo(category.lower(), name.lower())




schedule_library = [ScheduleInfo.from_str(fname) for fname in resource_listdir("flightanalysis", "data") if fname.endswith(".json")]


