from json import load, dump, JSONEncoder
from flightanalysis import State, Box, SchedDef, ManDef
from flightdata import Flight
from geometry import Transformation, Quaternion
import numpy as np
import pandas as pd

class NumpyEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        else:
            return JSONEncoder.default(self, obj)
    

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
#    with open(f'examples/scoring/manoeuvre/mans/{mdef.info.short_name}.json', 'w') as f:
#        dump(ma.to_dict(), f, cls=NumpyEncoder)

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


