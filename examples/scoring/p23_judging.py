from json import load
from flightanalysis import State, Box, SchedDef
from flightdata import Flight
import numpy as np
import pandas as pd
    
#examples/data/manual_F3A_P23_22_05_31_00000350.json
with open("examples/data/FC_P23_Template.json", "r") as f:
    data = load(f)


flight = Flight.from_fc_json(data)
box = Box.from_fcjson_parmameters(data["parameters"])
state = State.from_flight(flight, box).splitter_labels(data["mans"])
sdef = SchedDef.load(data["parameters"]["schedule"][1])

from flightanalysis import ScheduleAnalysis, ManoeuvreAnalysis

analysis = ScheduleAnalysis()
dgs = []

for mdef in sdef:
    ma = ManoeuvreAnalysis.build(mdef, state.get_manoeuvre(mdef.info.short_name))

    scores = ma.scores()
    if not scores.score() > 9.8:
        pass
    dgs.append(scores.summary())
    print(mdef.info.short_name, scores.score(), dgs[-1])

df = pd.DataFrame.from_dict(dgs)
print(df)
pass

#with open("_trials/temp/dgs.json", "w") as f:
#    dump(dgs)
#
#aligned.data.to_csv("_trials/temp/aligned.csv")
#intended_template.data.to_csv("_trials/temp/intended_template.csv")
#corrected_template.data.to_csv("_trials/temp/corrected_template.csv")


