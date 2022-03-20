from flightdata import Flight, Fields
from flightanalysis import Section, Box, get_schedule
from flightanalysis.schedule.elements.constructors import get_rates
from geometry import GPS

pilot = Flight.from_log("tests/test_inputs/test_log_pilot_position.BIN")
centre = Flight.from_log("tests/test_inputs/test_log_centre_position.BIN")

_p = pilot.read_fields(Fields.GLOBALPOSITION).iloc[-1]
p = GPS(_p.global_position_latitude, _p.global_position_longitude)

_c = centre.read_fields(Fields.GLOBALPOSITION).iloc[-1]
c = GPS(_c.global_position_latitude, _c.global_position_longitude)


box = Box.from_points("test_log_box", p,c)

box.to_json("tests/test_inputs/test_log_box.json")

flight = Flight.from_log("tests/test_inputs/test_log_00000052.BIN")


flight.to_csv("tests/test_inputs/test_log_00000052_flight.csv")



tx = flight.read_fields(Fields.TXCONTROLS)
tx = tx - tx.iloc[0]
tx = tx.iloc[:,:5]
tx.columns = ["throttle", "aileron_1", "aileron_2", "elevator", "rudder"]


section = Section.from_flight(flight, box).append_columns(tx)

section.to_csv("tests/test_inputs/test_log_00000052_section.csv")

scored = section.subset(100, 493)

p21 = get_schedule("F3A", "P21")

rates = get_rates(scored)
#direc = "left" if  scored[0].direction =="right" else "right"
template = p21.scale_distance(rates["distance"]).create_raw_template(scored[0].direction, rates["speed"], rates["distance"])

dist, aligned = Section.align(scored, template, 4)



aligned.to_csv("tests/test_inputs/test_log_00000052_aligned.csv")
#
#
intended = p21.match_intention(aligned)
#
from json import dump
with open("tests/test_inputs/intended_p21_0000052.csv", "w") as f:
    dump(intended.to_dict(), f)

from flightplotting.plots import plotdtw
plotdtw(intended.create_elm_matched_template(aligned), p21.manoeuvres).show()