from flightanalysis import Section
from flightplotting.plots import plotsec,plotdtw
from flightplotting.traces import axis_rate_trace
from examples.model import obj
from flightanalysis.schedule import p21
from flightanalysis.schedule.element import get_rates
from geometry import Points

flown = Section.from_flight("test/P21_new.csv", "test/gordano_box.json").subset(110, 505)

template = p21.scale_distance(170).create_template("right", 50.0, 170.0)

distance, aligned = Section.align(flown, template)


intented, intended_template = p21.match_intention(aligned)

#plotsec(intended_template, obj, 5).show()

for man in p21.manoeuvres:
    fig = plotsec(man.get_data(intended_template), obj, 5, color="orange")
    fig = plotsec(man.get_data(aligned), obj, 5, color="blue", fig=fig)
    fig.show()