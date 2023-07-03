from json import load
from flightanalysis import State, Box, get_schedule_definition, ManDef
from flightdata import Flight
from geometry import Transformation, Quaternion
import numpy as np
import pandas as pd

with open("examples/data/manual_F3A_P23_22_05_31_00000350.json", "r") as f:
    data = load(f)


flight = Flight.from_fc_json(data)
box = Box.from_fcjson_parmameters(data["parameters"])
state = State.from_flight(flight, box).splitter_labels(data["mans"])
sdef = get_schedule_definition(data["parameters"]["schedule"][1])

from flightanalysis import ScheduleAnalysis, ManoeuvreAnalysis

analysis = ScheduleAnalysis()
for mdef in sdef:
    analysis.add(ManoeuvreAnalysis.build(mdef, state.get_manoeuvre(mdef.info.short_name)))
    pass

dgs = []

for ma in analysis:
    inter_dgs =  ma.mdef.mps.collect(ma.intended)

    intra_dgs = ma.intended.analyse(ma.aligned,ma.intended_template)

    dgs.append(dict(
        inter = sum([dg.value for dg in inter_dgs]),
        intra = intra_dgs.downgrade()
    ))
    dgs[-1]["score"] = 10 - dgs[-1]["inter"] - dgs[-1]["intra"]
#    score = 10 - sum([dg.value for dg in inter_dgs]) - intra_dgs.downgrade()
 #   print(f"{p23[i].uid}: {score} ")


df = pd.DataFrame.from_dict(dgs)
print(df)
pass

#with open("_trials/temp/dgs.json", "w") as f:
#    dump(dgs)
#
#aligned.data.to_csv("_trials/temp/aligned.csv")
#intended_template.data.to_csv("_trials/temp/intended_template.csv")
#corrected_template.data.to_csv("_trials/temp/corrected_template.csv")


