from flightanalysis.data.p23 import create_p23
from flightanalysis.schedule.definition import SchedDef
from flightanalysis.schedule import Schedule
from flightdata import Flight
from flightanalysis import State, Box
from flightplotting import plotsec, plotdtw


#parse a flight
flown = State.from_flight(
    Flight.from_csv("examples/data/p23_example.csv").flying_only(), 
    Box.from_f3a_zone("examples/data/p23_box.f3a")
)[39:405]
wind=-1

#plotsec(flown).show()

#create the schedule definition
p23_def: SchedDef = create_p23(wind)
#
p23, template = p23_def.create_template(flown.pos.y.mean(), wind)

dist, aligned = State.align(flown, template)

#plotdtw(aligned, list(p23.manoeuvres.values())).show()


intended = p23.match_intention(aligned)


for i in range(17):

    dgs =  p23_def[i].mps.collect(intended[i])
    score = 10 - sum([sum(dg) for dg in dgs.values()])
    print(f"{p23_def[i].info.name}: {score}")

