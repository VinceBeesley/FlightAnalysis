from flightanalysis import SchedDef, State, Box
from flightdata import Flight


def parse_fcj(data: dict):
    flight = Flight.from_fc_json(data)
    box = Box.from_fcjson_parmameters(data["parameters"])
    state = State.from_flight(flight, box).splitter_labels(data["mans"])
    
    sdef = SchedDef.load(data["parameters"]["schedule"][1])
    return state, sdef


