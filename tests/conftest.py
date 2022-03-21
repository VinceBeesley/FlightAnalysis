import pytest
from flightdata import Flight
from flightanalysis.flightline import Box

@pytest.fixture(scope="session")
def whole_flight():
    return Flight.from_csv('tests/test_inputs/test_log_00000052_flight.csv')

@pytest.fixture(scope="session")
def flight(whole_flight):
    return whole_flight.flying_only()


@pytest.fixture(scope="session")
def box():
    return Box.from_json('tests/test_inputs/test_log_box.json')
#
#@pytest.fixture(scope="session")
#def p21():
#    return get_schedule(Categories.F3A, "P21")
#
#@pytest.fixture(scope="session")
#def seq(flight, box): 
#    return Section.from_flight(flight.flying_only(), box)
#
#@pytest.fixture(scope="session")
#def aligned():
#    return Section.from_csv("tests/test_inputs/test_log_00000052_aligned.csv")
#