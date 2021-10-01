from examples.schedules_construction.f_23 import f23 as sched
from json import dump


with open("flightanalysis/data/F23.json", "w") as f:
    dump(sched.to_dict(), f)
