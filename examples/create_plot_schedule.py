from flightanalysis import get_schedule, Categories, State
from flightplotting.plots import plotsec
from flightplotting.traces import boxtrace
from geometry import Transformation

f23 = get_schedule(Categories.F3A, "F23")


temp = f23.scale_distance(170)#.create_raw_template("right", 30.0, 170)

istate = State.from_transform(Transformation())



fig = plotsec(temp, 5, 2)
fig.add_trace(boxtrace()[0])

fig.show()


