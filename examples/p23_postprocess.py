from flightdata import Flight

from flightanalysis import State, Box, get_schedule
from flightplotting import plotsec, plotdtw
from os.path import exists
from geometry import Transformation, Point, Euler

p23 = get_schedule("F3A", "P23").scale_distance(170)
template = p23.create_raw_template("right", 30, 170, False)


if not exists("examples/data/p23_labelled_state.csv"):
    flight = Flight.from_csv("examples/data/p23_example.csv").flying_only()
    box = Box.from_f3a_zone("examples/data/p23_box.f3a")
    flown = State.from_flight(flight, box)[42:405]
    dist, aligned = State.align(flown, template, 5)
    aligned.to_csv("examples/data/p23_labelled_state.csv")
else:
    aligned = State.from_csv("examples/data/p23_labelled_state.csv")

intended = p23.match_intention(aligned)

elm = p23.manoeuvres[12].elements[7]
flwn = elm.get_data(aligned)
tmp = elm.get_data(template)

#
emat_template = intended.create_elm_matched_template(aligned)
mmat_template = intended.create_matched_template(aligned)
#
plotdtw(aligned, p23.manoeuvres).show()
plotdtw(emat_template, p23.manoeuvres).show()
plotdtw(mmat_template, p23.manoeuvres).show()


# TO be debugged....
corrected = intended.correct_intention()

cmat_template = corrected.create_matched_template(aligned)

plotdtw(cmat_template, p23.manoeuvres).show()
