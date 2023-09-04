from flightanalysis import ManoeuvreAnalysis as MA
from flightanalysis.analysis.manoeuvre_analysis import ElementAnalysis as EA
from json import load
import numpy as np

with open('examples/scoring/elements/mans/tHat.json', 'r') as f:
    ma = MA.from_dict(load(f))

from flightplotting import plotsec


ea = ma.e_0

dg = ea.el.intra_scoring.radius
res = dg(ea.fl, ea.tp, ea.ref_frame)

import plotly.graph_objects as go

fig = go.Figure()
x=list(range(0, len(res.measurement),1))
fig.add_trace(go.Scatter(x=x,y=abs(res.measurement.value), name='flown'))
fig.add_trace(go.Scatter(x=x, y=abs(res.measurement.expected), name='expected'))

vals = abs(dg.criteria.prepare(res.measurement.value, res.measurement.expected))
vals = dg.convolve(vals, 5)[5:-5]
fig.add_trace(go.Scatter(
    x=x[5:-5],
    y=vals, 
    name='vals',
    yaxis='y2'
))

fig.add_trace(go.Scatter(
    x=res.keys,
    y=np.array(vals)[np.array(res.keys)-5],
    text=np.round(res.dgs, 3),
    mode='markers+text',
    name='downgrades',
    yaxis='y2'
))


fig.update_layout(
    yaxis=dict(
        title='measurement',
        range=(0, 100)
    ),
    yaxis2=dict(
        title='ratio',
        overlaying="y",
        side="right",
        range=(0,2)
    )
)

fig.show()

pass