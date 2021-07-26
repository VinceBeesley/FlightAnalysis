from flightanalysis import Section
from flightplotting.plots import plotsec, plotdtw
from flightplotting.traces import axis_rate_trace
from examples.model import obj
from flightanalysis.schedule import p21
from flightanalysis.schedule.element import get_rates
from geometry import Points, Transformation, Point, Quaternion
import numpy as np
flown = Section.from_flight(
    "test/P21_new.csv", "test/gordano_box.json").subset(110, 505)

rates = get_rates(flown)

template = p21.scale_distance(170).create_raw_template("right", 50.0, 170.0)

distance, aligned = Section.align(flown, template)

intended, intended_template = p21.match_intention(aligned)

istate = flown.get_state_from_index(0)

ptrans = intended.create_itransform(
    -np.sign(flown.get_state_from_index(0).transform.point(Point(1, 0, 0)).x),
    istate.pos.y
)


templates = []
# TODO add exit line on construction
for manoeuvre in intended.manoeuvres:
    templates.append(manoeuvre.create_template(
        manoeuvre.get_data(intended_template).get_state_from_index(0).transform, rates["speed"]
    ))
    

scaled_template =  Section.stack(templates)

#plotsec(intended_template, obj, 5).show()

for man in p21.manoeuvres:
    fig = plotsec(man.get_data(aligned), obj, 5, color="orange")
    fig = plotsec(man.get_data(intended_template), obj, 5, color="red", fig=fig)
    fig.show()

    fig = plotsec(man.get_data(aligned), obj, 5, color="orange")
    fig = plotsec(man.get_data(scaled_template), obj, 5, color="red", fig=fig)
    fig.show()


