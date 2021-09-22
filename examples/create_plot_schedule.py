from flightanalysis.schedule import p21, f21, p23, f23
from flightplotting.plots import plotsec
from flightplotting.traces import boxtrace
from examples.model import obj


temp = f23.scale_distance(170).create_raw_template("right", 30.0, 170)
fig = plotsec(temp, obj, 5, 2)
fig.add_trace(boxtrace()[0])

fig.show()