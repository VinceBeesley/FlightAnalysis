from pathlib import Path

from flightanalysis.schedule import SchedDef
from pkg_resources import resource_stream
from json import loads


def get_schedule_definition(name):
    data = resource_stream(__name__, f"{name.lower()}.json").read().decode()
    return SchedDef.from_dict(loads(data))
