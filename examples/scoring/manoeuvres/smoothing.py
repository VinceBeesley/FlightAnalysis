from flightanalysis import ManoeuvreAnalysis as MA
from flightanalysis.analysis.manoeuvre_analysis import ElementAnalysis as EA
from json import load, dumps
import numpy as np

with open('examples/scoring/manoeuvres/mans/tHat.json', 'r') as f:
    ma = MA.from_dict(load(f))

from flightplotting import plotsec


ea = ma.e_0

dg = ea.el.intra_scoring.radius
res = dg(ea.fl, ea.tp, ea.ref_frame)


from flightanalysis.schedule.scoring.downgrade import butter_filter


import plotly.graph_objects as go


x=list(range(0, len(res.measurement)))


fig = go.Figure()
raw = abs(res.measurement.value)
fig.add_trace(go.Scatter(x=x,y=raw, name='raw'))
fig.add_trace(go.Scatter(x=x[6:-6], y=butter_filter(raw[6:-6], 10), name='butter cutoff 10Hz'))
fig.add_trace(go.Scatter(x=x[6:-6], y=butter_filter(raw[6:-6], 3), name='butter cutoff 2Hz'))

fig.show()



