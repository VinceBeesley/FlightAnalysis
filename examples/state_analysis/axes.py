from flightanalysis import State, Environment, Time
from geometry import Transformation, P0, Euldeg, PY, PX, Point
from flightplotting import plotsec
import numpy as np
from flightanalysis import Coefficients, Environment, Environment, Flow
from flightanalysis.model import cold_draft
import plotly.express as px


judging = State.from_transform(
    Transformation(P0(), Euldeg(180,0,0)), 
    vel=PX(20), rvel=np.pi * Point(0.25, 0.25, 0)
).extrapolate(6, 3)

env = Environment.from_constructs(Time.now(), wind=PY(5))

wind = judging.judging_to_wind(env)



flow = Flow.build(wind, env)
coeffs = Coefficients.build(wind, flow.q, cold_draft)


flow = flow.rotate(coeffs, 10, 5)
px.line(np.degrees(flow.flow.to_pandas().iloc[:,:-1])).show()

body = wind.wind_to_body(flow)


fig = plotsec([judging, wind, body], nmodels=10, scale=3)
fig.show()
