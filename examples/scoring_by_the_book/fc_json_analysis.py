from json import load
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

ma = ManoeuvreAnalysis.build(sdef[mid], state.get_meid(mid+1))

ma.intra_dgs = ma.intended.analyse(ma.aligned, ma.intended_template)
ma.intra_dg = ma.intra_dgs.downgrade()

ma.inter_dgs = ma.mdef.mps.collect(ma.intended)
ma.inter_dg = sum([dg.value for dg in ma.inter_dgs])





ma.plot_3d().show()