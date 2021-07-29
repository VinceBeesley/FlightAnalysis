from flightanalysis import Section
from flightplotting.plots import plotsec, plotdtw
from flightplotting.traces import axis_rate_trace
from examples.model import obj
from flightanalysis.schedule import p21
from flightanalysis.schedule.element import get_rates
from geometry import Points, Transformation, Point, Quaternion
import numpy as np
flown = Section.from_flight(
    "test/P21_new.csv", "test/gordano_box.json").subset(106, 505)

rates = get_rates(flown)

template = p21.scale_distance(170).create_raw_template("right", 50.0, 170.0)

distance, aligned = Section.align(flown, template)

plotdtw(p21.manoeuvres[0].get_data(aligned), p21.manoeuvres[0].elements).show()

intended = p21.match_intention(aligned).correct_intention()


scaled_template =  intended.create_matched_template(aligned)

#plotsec(intended_template, obj, 5).show()

for man in p21.manoeuvres:
    fig = plotsec(man.get_data(aligned), obj, 5, color="orange")
    fig = plotsec(man.get_data(scaled_template), obj, 5, color="red", fig=fig)
    fig.show()


