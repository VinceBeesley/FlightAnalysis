from examples.schedules_construction.p_21 import p21
from examples.schedules_construction.f_21 import f21
from examples.schedules_construction.p_23 import p23
from examples.schedules_construction.f_23 import f23
from json import dump

for sched in [p21, p23, f21, f23]:
    with open("flightanalysis/data/{}.json".format(sched.name), "w") as f:
        dump(sched.to_dict(), f)
