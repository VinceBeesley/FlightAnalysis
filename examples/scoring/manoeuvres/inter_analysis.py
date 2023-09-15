from flightanalysis import ManoeuvreAnalysis as MA
from flightanalysis.analysis.manoeuvre_analysis import ElementAnalysis as EA
from json import load, dumps
import numpy as np

with open('examples/scoring/manoeuvres/mans/tHat.json', 'r') as f:
    ma = MA.from_dict(load(f))

from flightplotting import plotsec


resrr = ma.mdef.mps.partial_roll_rate.get_downgrades(ma.intended.elements)

res = ma.mdef.mps.collect(ma.intended, ma.intended_template)

print(res.downgrade_df())

print(res.total)

print(res.line_length.summary_df())
pass