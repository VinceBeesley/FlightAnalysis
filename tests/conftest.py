import pytest
from flightdata import Flight
from flightanalysis import Box
from flightanalysis.schedule import Schedule, Categories, get_schedule, Line
from flightanalysis import Section

@pytest.fixture(scope="session")
def flight():
    return Flight.from_csv('tests/test_inputs/test_log_00000052_flight.csv')

@pytest.fixture(scope="session")
def box():
    return Box.from_json('tests/test_inputs/test_log_box.json')

@pytest.fixture(scope="session")
def p21():
    return get_schedule(Categories.F3A, "P21")

@pytest.fixture(scope="session")
def seq(flight, box): 
    return Section.from_flight(flight, box)

@pytest.fixture(scope="session")
def aligned():
    return Section.from_csv("tests/test_inputs/test_log_00000052_aligned.csv")
