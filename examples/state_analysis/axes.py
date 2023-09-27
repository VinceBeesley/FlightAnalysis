from flightanalysis import State, Environment, Time
from geometry import Transformation, P0, Euldeg, PY, PX
from flightplotting import plotsec

st = State.from_transform(Transformation(P0(), Euldeg(180, 0, 0)), vel=PX(20)).extrapolate(5)


env = Environment.from_constructs(Time.now(), wind=PY(5))

wind = st.judging_to_wind(env)

fig = plotsec([st, wind], nmodels=10, scale=3)
fig.show()