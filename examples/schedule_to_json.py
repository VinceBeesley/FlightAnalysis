from flightanalysis.data.p23 import create_p23
from flightanalysis.schedule.definition.schedule_definition import SchedDef

from json import dump


p23_def:SchedDef = create_p23(1)
sched, template = p23_def.create_template(180, 1)


