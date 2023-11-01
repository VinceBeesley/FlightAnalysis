import unittest
from flightanalysis.schedule import Schedule
from flightanalysis.state import State
from json import load

from flightdata import Flight

from pytest import approx, fixture, mark
import warnings
warnings.filterwarnings("error")

@fixture(scope="session")
def schedule_json():
    with open("flightanalysis/data/P21.json", "r") as f:
        return load(f)

@fixture(scope="session")
def schedule(schedule_json):   
    return Schedule(**schedule_json)

@fixture(scope="session")
def aligned():
    return State.from_csv("tests/test_inputs/test_log_00000052_aligned.csv")



def test_create_raw_template(schedule):
    sched = schedule.scale_distance(170.0)
    out = sched.create_raw_template("left", 30.0, 170.0)

    assert isinstance(out, State)

    stallturn = schedule.manoeuvres[1].get_data(out)

    assert len(set(stallturn.element)) == 10
    



def test_from_splitter():
    with open("tests/test_inputs/manual_F3A_P21_21_09_24_00000052.json", 'r') as f:
        fcj = load(f)
    box = FCJson.read_box(fcj["name"], fcj['parameters'])
    flight = Flight.from_fc_json(fcj)
    sec = State.from_flight(flight, box)

    sched = get_schedule(*fcj["parameters"]["schedule"])
    labelled = sched.label_from_splitter(sec, fcj["mans"])

    assert isinstance(labelled, State)
    assert sec.duration /2  == approx(labelled.duration/2, 1)
    


def test_get_subset(schedule, aligned):
    subset = schedule.get_subset(aligned, 3, 5)

    assert subset.duration < aligned.duration

    assert max(subset.data.manoeuvre) == schedule.manoeuvres[4].uid
    assert min(subset.data.manoeuvre) == schedule.manoeuvres[3].uid

#def test_set_withcopy(self):
    