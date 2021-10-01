import unittest
from flightanalysis.schedule import Schedule, get_schedule, LineEl, Categories
from flightanalysis.schedule.element import get_rates
from flightanalysis import Section
from json import load
from flightanalysis.fc_json import FCJson
from flightdata import Flight
import pytest



@pytest.fixture(scope="session")
def schedule_json():
    with open("schedules/F21.json", "r") as f:
        return load(f)

@pytest.fixture(scope="session")
def schedule(schedule_json):
    
    return Schedule(**schedule_json)

def test_schedule(schedule):
    assert schedule.category == Categories.F3A


def test_create_raw_template(schedule):
    sched = schedule.scale_distance(170.0)
    out = sched.create_raw_template("left", 30.0, 170.0)

    assert isinstance(out, Section)

    stallturn = schedule.manoeuvres[1].get_data(out)

    assert len(stallturn.element.unique()) == 10
    


def test_match_axis_rate(schedule):
    
    sec = Section.from_csv("tests/test_inputs/test_log_00000052_section.csv").subset(110, 200)

    rates = get_rates(sec)

    rate_matched = schedule.match_rates(rates)

    for manoeuvre in rate_matched.manoeuvres:
        for i, elm in enumerate(manoeuvre.elements):
            if isinstance(elm, LineEl):

                assert elm.length > 0.0, "manoeuvre {}, elm {}, length {}".format(manoeuvre.name, i, elm.length)

def test_from_splitter():
    with open("tests/test_inputs/manual_F3A_P21_21_09_24_00000052.json", 'r') as f:
        fcj = load(f)
    box = FCJson.read_box(fcj["name"], fcj['parameters'])
    flight = Flight.from_fc_json(fcj)
    sec = Section.from_flight(flight, box)

    sched = get_schedule(*fcj["parameters"]["schedule"])
    labelled = sched.label_from_splitter(sec, fcj["mans"])

    assert isinstance(labelled, Section)
    pytest.approx(sec.duration /2 , labelled.duration/2)
    


