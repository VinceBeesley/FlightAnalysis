
from flightanalysis.schedule.definition import *
from flightanalysis.criteria import *
from pytest import fixture


@fixture
def mp():
    return ManParm("length", inter_f3a_length, 20.0)

def test_mp_value(mp):
    assert mp.value == 20

