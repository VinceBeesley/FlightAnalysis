from flightanalysis import ManoeuvreAnalysis as MA
from flightanalysis.analysis.manoeuvre_analysis import ElementAnalysis as EA
from json import load, dumps
import numpy as np

with open('examples/scoring/manoeuvres/mans/tHat.json', 'r') as f:
    ma = MA.from_dict(load(f))

from flightplotting import plotsec
from flightplotting.traces import vectors
from flightanalysis.schedule.scoring import Result, DownGrade

ea = ma.e_0

dg: DownGrade = ea.el.intra_scoring.roll_angle
res: Result = dg(ea.fl, ea.tp, ea.ref_frame)

res.plot().show()

fig = ea.plot_3d()

fig.add_traces(vectors(10, ea.fl, -res.measurement.direction * np.degrees(res.sample)))
fig.show()
pass