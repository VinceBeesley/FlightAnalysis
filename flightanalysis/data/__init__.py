from pathlib import Path
from .p23 import create_p23
from flightanalysis.schedule import SchedDef

creators = dict(
    p23=create_p23
)


jsons = {p.stem: p  for p in Path(__file__).parent.glob("*.json")}


def get_schedule_definition(name):
    return SchedDef.from_json(jsons[name.lower()])


