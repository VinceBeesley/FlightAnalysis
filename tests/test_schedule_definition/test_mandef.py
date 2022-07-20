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


def test_rollcombo():
    rc = rollcombo(
        [
            Roll(0.25, 1, 1), 
            Roll(0.25, 1, 1)
        ], 
        30, 500, 5,
        RollPosition.CENTRE
    )

    assert len(rc) == 5
    assert rc[0].rolls==0
    assert rc[1].rolls==0.25


def test_roll():
    rc = roll("3X4", 30, 500, 5, 1, RollPosition.CENTRE)
    assert len(rc) == 7




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
                Loop(s, 2*r0, -0.25),
                Line(s, l1, 0),
                Loop(s, 2*r0, 0.25)
            ]
    )

def test_generator(vline):
    elms = vline.generator(50, 100, 30)
    assert elms[0].diameter == 100
    assert isinstance(elms[0], Loop)



def compile_elms(*args):
    elms = []
    for arg in args:
        if isinstance(arg, El):
            elms.append(arg)
        else:
            elms += arg
    return elms


@fixture
def tophat():
    ManDef(
        "tophat",
        4,
        BoxLocation(Height.BTM, Direction.UPWIND, Orientation.UPRIGHT),
        Position.CENTRE,
        2,
        lambda s, r0, l1, p, a0, l2:
            compile_elms(
                Loop(s, r0*2, -0.25, 0),
                roll("2X4", s, l1, p, a0, RollPosition.CENTRE),
                Loop(s, r0*2, -0.25),
                roll("1/2", s, l2, p, a0, RollPosition.CENTRE),
                Loop(s, r0*2, 0.25, 0),
                roll("2X4", s, l1, p, a0, RollPosition.CENTRE),
                Loop(s, r0*2, 0.25)
            )
    )







@fixture
def p23():
    return SchedDef.parse("tests/test_inputs/p23_def_2.sched")

def test_parse_schedule(p23):
    
    assert p23.defs[0].name=="tophat"
    assert p23.defs[0].segments[0].radius == None
    assert p23.defs[0].segments[0].length == "l0"
    