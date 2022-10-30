
from flightanalysis.schedule.definition import *
from flightanalysis.criteria import *
from pytest import fixture


@fixture
def mp():
    return ManParm("length", inter_f3a_length, 20.0, [lambda els : 10, lambda els : 20])

def test_mp_value(mp):
    assert mp.value == 20

def test_mp_collect(mp):
    np.testing.assert_array_equal(mp.collect(1), [10, 20]) 

def test_mp_get_downgrades(mp):
    res = mp.get_downgrades(1)
    np.testing.assert_array_equal(res.downgrades, [0,2])
    assert res.downgrade == 2


