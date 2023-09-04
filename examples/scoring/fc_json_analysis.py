from json import load, dump
from flightanalysis import State, Box, ManoeuvreAnalysis, SchedDef
from flightdata import Flight
import numpy as np
import pandas as pd
from geometry import Point
from flightanalysis.schedule.scoring import *
from flightanalysis.schedule.definition.manoeuvre_info import Position

with open("examples/data/manual_F3A_P23_22_05_31_00000350.json", "r") as f:
    data = load(f)


flight = Flight.from_fc_json(data)
box = Box.from_fcjson_parmameters(data["parameters"])
state = State.from_flight(flight, box).splitter_labels(data["mans"])

sdef = SchedDef.load(data["parameters"]["schedule"][1])

mid = 9

mdef = sdef[mid]
print(mdef.info.name)
flown = state.get_manoeuvre(mid+1)

ma = ManoeuvreAnalysis.build(mdef, flown)

    
if False:
    def npconverter(o):
        if isinstance(o, np.ndarray):
            return o.tolist()
    with open("examples/scoring/manoeuvre/ma.json", "w") as f:
        dump(ma.to_dict(), f, default=npconverter)


ma.plot_3d(nmodels=5).show()

ma.intra_dgs = ma.intended.analyse(ma.aligned, ma.intended_template)
ma.intra_dg = ma.intra_dgs.downgrade()
df = ma.intra_dgs.downgrade_df()

print("Intra DGS:")

print(df)

ma.inter_dgs = ma.mdef.mps.collect(ma.intended)
ma.inter_dg = sum([dg.value for dg in ma.inter_dgs])

inter = ma.inter_dgs.downgrade_df()
print("Inter DGS:")

print(inter)
print(inter.sum())


print(f"intra = {df.sum().Total}")
print(f"inter = {inter.sum().sum()}")

positioning = ma.side_box()
print(f"{positioning.name} = {positioning.value}")

top_box = ma.top_box()
print(f"top box = {top_box.value}")


distance = ma.distance()
print(f"distance = {distance.value}")

print("Total:")
print(10 - df.sum().Total - inter.sum().sum() - positioning.value - top_box.value)
pass




