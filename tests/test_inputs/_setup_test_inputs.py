from flightdata import Flight, Fields
from flightanalysis import Section, Box
from geometry import GPSPosition

pilot = Flight.from_log("tests/test_inputs/test_log_pilot_position.BIN")
centre = Flight.from_log("tests/test_inputs/test_log_centre_position.BIN")

_p = pilot.read_fields(Fields.GLOBALPOSITION).iloc[-1]
p = GPSPosition(_p.global_position_latitude, _p.global_position_longitude)

_c = centre.read_fields(Fields.GLOBALPOSITION).iloc[-1]
c = GPSPosition(_c.global_position_latitude, _c.global_position_longitude)


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

