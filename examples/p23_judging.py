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
for i in range(17):
    for mp in p23_def[i].mps.parms.values(): 
        flown_parm = mp.collect(intended[i].all_elements)
        if len(flown_parm) >0:
            if isinstance(mp.criteria, Combination):
                mp.default = mp.criteria.check_option(flown_parm)
            else:
                mp.default = np.mean(flown_parm)
p23_corr, corrected_template = p23_def.create_template(flown.pos.y.mean(), wind)


#correct the roll directions in the intended template
#TODO this should be part of the match intention method?
nmans = []
for mcor, mfl in zip(p23_corr, intended):
    nels=[]
    for ecor, efl in zip(mcor.all_elements, mfl.all_elements):
        if isinstance(ecor, Line):
            nels.append(efl.set_parms(roll=abs(efl.roll) * np.sign(ecor.roll)))
        elif isinstance(ecor, Loop):
            nels.append(efl.set_parms(roll=abs(efl.roll) * np.sign(ecor.roll)))
            nels.append(efl.set_parms(roll=abs(efl.angle) * np.sign(ecor.angle)))
        elif isinstance(ecor, Snap):
            nels.append(efl.set_parms(roll=abs(efl.rolls) * np.sign(ecor.rolls)))
        else:
            nels.append(efl.set_parms())
    nmans.append(Manoeuvre.from_all_elements(nels))

intended_sched = Schedule(nmans)

intended_template = intended_sched.create_template(Transformation(
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


