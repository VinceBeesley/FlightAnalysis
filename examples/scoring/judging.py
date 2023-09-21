from json import load
from flightanalysis import State, Box, SchedDef
from flightdata import Flight
import numpy as np
import pandas as pd
    
with open("examples/data/manual_F3A_P23_22_05_31_00000350.json", "r") as f:
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



