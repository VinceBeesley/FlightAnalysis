from pathlib import Path

from flightanalysis.schedule import SchedDef
from .p23 import p23_def
from .p25 import p25_def

jsons = {p.stem: p  for p in Path(__file__).parent.glob("*.json")}


def get_schedule_definition(name):
    return SchedDef.from_json(jsons[name.lower()])


