from flightanalysis import State
from geometry import Transformation, P0, Euldeg, PX, Point
from flightplotting import plotsec
from flightplotting.traces import vectors
import numpy as np


st = State.from_transform(
    Transformation(P0(), Euldeg(180,0,0)), 
    vel=PX(20), rvel=np.pi * Point(0.25, 0.25, 0)
).extrapolate(6, 3)


fig = plotsec(st, scale=2, nmodels=5)

fig.add_traces(vectors(20, st, 0.5*st.body_to_world(st.acc, True)))

fig.add_traces(vectors(20, st, 5*st.body_to_world(st.rvel, True), line=dict(color="green")))

fig.show()


