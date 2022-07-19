from pytest import fixture


from flightanalysis.schedule.definition import (
    SchedDef,
    ManDef, 
    Orientation, 
    Direction, 
    Height, 
    Position,
    BoxLocation
)
from flightanalysis.schedule.elements import *





@fixture
def vline():
    return ManDef(
        "vline",
        2,
        BoxLocation(Height.BTM, Direction.UPWIND, Orientation.UPRIGHT),
        Position.CENTRE,
        2,
        lambda r0, l1, s:
            [
                Loop(1, s, 2*r0, -0.25),
                Line(2, s, l1, 0),
                Loop(1, s, 2*r0, 0.25)
            ]
    )

def test_generator(vline):
    elms = vline.generator(50, 100, 30)
    assert elms[0].diameter == 100
    assert isinstance(elms[0], Loop)


@fixture
def tophat():
    ManDef(
        "tophat",
        4,
        BoxLocation(Height.BTM, Direction.UPWIND, Orientation.UPRIGHT),
        Position.CENTRE,
        2,
        lambda r0, :
            [
                Loop(  0.3, -0.25),
            ] + rollmaker(2, "X", 4, 0.4, "Centre") + [
                Loop(  0.3, -0.25),
            ] + rollmaker(1, "/", 2, 0.4, "Centre") + [
                Loop(  0.3, 0.25),
            ] + rollmaker(2, "X", 4, 0.4, "Centre") + [
                Loop(  0.3, 0.25)   # 0.5
            ]
    )




@fixture
def p23():
    return SchedDef.parse("tests/test_inputs/p23_def_2.sched")

def test_parse_schedule(p23):
    
    assert p23.defs[0].name=="tophat"
    assert p23.defs[0].segments[0].radius == None
    assert p23.defs[0].segments[0].length == "l0"
    