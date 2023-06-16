import numpy as np
import pandas as pd

from flightanalysis import get_schedule_definition
from flightdata import Flight
from flightanalysis import State, Box
from geometry import Transformation

p23_def = get_schedule_definition("p23")

#parse a flight, cutoff takeoff and landing
flown = State.from_flight(
    Flight.from_csv("examples/data/p23_example.csv").flying_only(), 
    Box.from_f3a_zone("examples/data/p23_box.f3a")
)[39:405]

wind=-1

#create the schedule definition, schedule and template
p23, template = p23_def.create_template(flown.pos.y.mean(), wind)


#align the template to the flight
dist, aligned = State.align(flown, template)

#plotdtw(aligned, list(p23.manoeuvres.values())).show()
#update the schedule to match the flight
intended = p23.match_intention(template[0].transform, aligned)

#correct the intended inter element parameters to make a corrected shcedule and template
p23_def.update_defaults(intended)
corrected, corrected_template = p23_def.create_template(flown.pos.y.mean(), wind)

#correct the roll directions in the intended template
intended = intended.copy_directions(corrected)

intended_template = intended.create_template(Transformation(
    aligned[0].pos,
    aligned[0].att.closest_principal()
))


dgs = []

for i in range(17):
    inter_dgs =  p23_def[i].mps.collect(intended[i])

    intra_dgs = intended[i].analyse(
        intended[i].get_data(aligned),
        intended[i].get_data(intended_template)
    )

    dgs.append(dict(
        inter = sum([dg.value for dg in inter_dgs]),
        intra = intra_dgs.downgrade()
    ))

#    score = 10 - sum([dg.value for dg in inter_dgs]) - intra_dgs.downgrade()
 #   print(f"{p23[i].uid}: {score} ")


df = pd.DataFrame.from_dict(dgs)
pass

#with open("_trials/temp/dgs.json", "w") as f:
#    dump(dgs)
#
#aligned.data.to_csv("_trials/temp/aligned.csv")
#intended_template.data.to_csv("_trials/temp/intended_template.csv")
#corrected_template.data.to_csv("_trials/temp/corrected_template.csv")


