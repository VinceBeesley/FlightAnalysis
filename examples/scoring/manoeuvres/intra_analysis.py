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

import plotly.graph_objects as go

fig = go.Figure()
x=list(range(0, len(res.measurement),1))
fig.add_trace(go.Scatter(x=x,y=abs(res.measurement.value), name='flown'))
fig.add_trace(go.Scatter(x=x, y=abs(res.measurement.expected), name='expected'))


fig.add_trace(go.Scatter(
    x=x,
    y=res.sample, 
    name='sample',
    yaxis='y',
    line=dict(width=3)
))

hovtxt=[res.info(i) for i in range(len(res.keys))]

fig.add_trace(go.Scatter(
    x=res.keys,
    y=res.sample[res.keys],
    text=np.round(res.dgs, 3),
    hovertext=hovtxt,
    mode='markers+text',
    name='downgrades',
    yaxis='y'
))


fig.update_layout(
    yaxis=dict(
        title='measurement',
    )
)

fig.show()

pass