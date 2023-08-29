from flightanalysis.schedule.elements import Loop, Line, Elements
from flightanalysis.schedule.scoring.measurement import Measurement
import numpy as np
from flightanalysis import State, Manoeuvre
from geometry import Transformation, PX, Point, Euldeg
import plotly.graph_objects as go
from flightplotting import plotsec


loop = Loop(30, 100, np.radians(360), uid='loop')
ist = State.from_transform(Transformation(
    Point(100, 150, 0),
    Euldeg(180, 0, 0)
))

tp = loop.create_template(ist)


fl = Manoeuvre.from_all_elements( 'test',  Elements([
    Loop(30, 100, np.radians(180), uid="loop"),
    Loop(30, 100, np.radians(180), uid="loop2")
])).create_template(ist)

fl.data.element='loop'

tp = loop.create_template(ist, fl.time)

fig = plotsec(fl, nmodels=5)

fig = plotsec(tp, fig=fig)
fig.add_trace(go.Scatter3d(x=[0],y=[0],z=[0], mode='markers'))
fig.show()
meas = Measurement.roll_angle(fl, tp, tp[0].transform)

import plotly.graph_objects as go


fig = go.Figure()
fig.add_trace(go.Scatter(y=meas.visibility, name='visibility'))
fig.add_trace(go.Scatter(y=abs(meas.value), name='value'))
fig.show()

pass