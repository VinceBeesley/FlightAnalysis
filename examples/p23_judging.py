from flightanalysis.data.p23 import create_p23
from flightanalysis.schedule.definition import SchedDef
from flightanalysis.schedule import Schedule, Manoeuvre
from flightdata import Flight
from flightanalysis import State, Box
from flightplotting import plotsec, plotdtw
from flightanalysis.criteria.local import Combination 
import numpy as np
from flightanalysis import Line, Loop, Spin, StallTurn, Snap
from geometry import Transformation
from json import dump
from flightanalysis.schedule.definition import ManParms, ManDef, ElDef, ElDefs

#parse a flight, cutoff takeoff and landing
flown = State.from_flight(
    Flight.from_csv("examples/data/p23_example.csv").flying_only(), 
    Box.from_f3a_zone("examples/data/p23_box.f3a")
)[39:405]

wind=-1



#create the schedule definition, schedule and template
p23_def = create_p23(wind)

p23, template = p23_def.create_template(flown.pos.y.mean(), wind)


#align the template to the flight
dist, aligned = State.align(flown, template)

#plotdtw(aligned, list(p23.manoeuvres.values())).show()
#update the schedule to match the flight
intended = p23.match_intention(aligned)

#correct the intended inter element parameters to make a corrected shcedule and template
p23_def.update_defaults(intended)
corrected, corrected_template = p23_def.create_template(flown.pos.y.mean(), wind)

#correct the roll directions in the intended template
intended = intended.copy_directions(corrected)

intended_template = intended.create_template(Transformation(
    aligned[0].pos,
    aligned[0].att.closest_principal()
))


for i in range(17):
    dgs =  p23_def[i].mps.collect(intended[i])
    score = 10 - sum([sum(dg) for dg in dgs.values()])
    print(f"{p23[i].uid}: {score} ")


#with open("_trials/temp/dgs.json", "w") as f:
#    dump(dgs)
#
#aligned.data.to_csv("_trials/temp/aligned.csv")
#intended_template.data.to_csv("_trials/temp/intended_template.csv")
#corrected_template.data.to_csv("_trials/temp/corrected_template.csv")


