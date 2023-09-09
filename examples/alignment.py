from json import load, dump, JSONEncoder
from flightanalysis import State, Box, SchedDef, ManDef
from flightdata import Flight
from geometry import Transformation, Quaternion
import numpy as np
import pandas as pd
    

with open("examples/data/manual_F3A_P23_23_08_11_00000094.json", "r") as f:
    data = load(f)


flight = Flight.from_fc_json(data)
box = Box.from_fcjson_parmameters(data["parameters"])
state = State.from_flight(flight, box).splitter_labels(data["mans"])
sdef = SchedDef.load(data["parameters"]["schedule"][1])

from flightanalysis import ScheduleAnalysis, ManoeuvreAnalysis

analysis = ScheduleAnalysis()
dgs = []


mdef = sdef.sFin
flown = state.get_manoeuvre(mdef.info.short_name)

itrans = ManoeuvreAnalysis.initial_transform(mdef, flown)
man, tp = ManoeuvreAnalysis.template(mdef, itrans)
aligned = ManoeuvreAnalysis.alignment(tp, man, flown)[1]

from flightplotting import plotdtw

plotdtw(aligned, aligned.data.element.unique()).show()

pass

#with open("_trials/temp/dgs.json", "w") as f:
#    dump(dgs)
#
#aligned.data.to_csv("_trials/temp/aligned.csv")
#intended_template.data.to_csv("_trials/temp/intended_template.csv")
#corrected_template.data.to_csv("_trials/temp/corrected_template.csv")


