from json import load, dump
from flightanalysis import State, Box, get_schedule_definition, ManoeuvreAnalysis
from flightdata import Flight
import numpy as np
import pandas as pd


with open("examples/data/manual_F3A_P23_22_05_31_00000350.json", "r") as f:
    data = load(f)


flight = Flight.from_fc_json(data)
box = Box.from_fcjson_parmameters(data["parameters"])
state = State.from_flight(flight, box).splitter_labels(data["mans"])

sdef = get_schedule_definition(data["parameters"]["schedule"][1])

mid = 0

mdef = sdef[mid]
flown = state.get_manoeuvre(mid+1)

ma = ManoeuvreAnalysis.build(mdef, flown)

    
if False:
    def npconverter(o):
        if isinstance(o, np.ndarray):
            return o.tolist()
    with open("examples/scoring/manoeuvre/tophat_analysis.json", "w") as f:
        dump(ma.to_dict(), f, default=npconverter)


ma.plot_3d(nmodels=5).show()

ma.intra_dgs = ma.intended.analyse(ma.aligned, ma.intended_template)
ma.intra_dg = ma.intra_dgs.downgrade()
df = ma.intra_dgs.downgrade_df()
print(df)
print(df.sum())
ma.inter_dgs = ma.mdef.mps.collect(ma.intended)
ma.inter_dg = sum([dg.value for dg in ma.inter_dgs])

inter = ma.inter_dgs.downgrade_df()
print(inter)
print(inter.sum())
print(inter.sum().sum())


print(10 - df.sum().Total - inter.sum().sum())
pass




