
from flightanalysis.schedule.definition import *
from flightanalysis.schedule.scoring import *
from flightanalysis.schedule.elements import *
from pytest import fixture

 
@fixture
def mp():
    return ManParm(
        "length", 
        inter_f3a_length, 
        20.0,
        Collectors([
            Collector("e1", "length"),
            Collector("e2", "length")
        ])
    )

@fixture
def els(mp):
    return Elements([
        Line(30, 30, 0, "e1"),
        Line(30, 10, 0, "e2")
    ])

def test_mp_value(mp):
    assert mp.value == 20

def test_mp_collect(mp, els):
    np.testing.assert_array_equal(mp.collect(els), [30, 10]) 

def test_mp_get_downgrades(mp, els):
    res = mp.get_downgrades(els)
    np.testing.assert_array_equal(res.downgrades, [0,1.6])
    assert res.value == 1.6


