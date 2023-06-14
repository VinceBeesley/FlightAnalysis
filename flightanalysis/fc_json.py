from flightanalysis.state import State
from flightanalysis.flightline import Box
from flightanalysis.data import get_schedule_definition
from flightdata import Flight


def parse_fcj(data: dict):
    flight = Flight.from_fc_json(data)
    box = Box.from_fcjson_parmameters(data["parameters"])
    state = State.from_flight(flight, box).splitter_labels(data["mans"])
    
    sdef = get_schedule_definition(data["parameters"]["schedule"][1])
    return state, sdef


