from pytest import fixture


from flightanalysis.schedule.definition import (
    SchedDef,
    ManDef, 
    ElmDef, 
    Orientation, 
    Direction, 
    Height, 
    Position,
    ElType
)
from flightanalysis.schedule.elements import *

@fixture
def p23():
    return SchedDef.parse("tests/test_inputs/p23_def_2.sched")

def test_parse_schedule(p23):
    
    assert p23.defs[0].name=="tophat"
    assert p23.defs[0].elms[0].radius == None
    assert p23.defs[0].elms[0].length == "l0"
    