from flightanalysis.schedule.elements import Loop, Line
from flightanalysis.schedule.scoring.measurement import Measurement
import numpy as np
from flightanalysis import State
from geometry import Transformation, PX, Point, Euldeg
import plotly.graph_objects as go

from flightplotting import plotsec


line = Line(30, 100, np.radians(90))
ist = State.from_transform(Transformation(
    Point(0, 150, 0),
    Euldeg(180, 0, 0)
))

tp = line.create_template(ist)

fl = Loop(30, 1000, np.radians(10),  np.radians(90), ke=False).create_template(ist)

line = line.match_intention(ist.transform, fl)

tp = line.create_template(ist, fl.time)

fig = plotsec(fl, nmodels=5)

fig = plotsec(tp, fig=fig)
fig.add_trace(go.Scatter3d(x=[0], y=[0], z=[0], mode='markers'))
fig.show()
meas = Measurement.track_z(fl, tp, tp[0].transform)



fig = go.Figure()
fig.add_trace(go.Scatter(y=meas.visibility, name='vis'))
fig.add_trace(go.Scatter(y=abs(meas.value), name='measure'))
fig.show()

pass