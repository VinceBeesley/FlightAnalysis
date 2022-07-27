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

from flightanalysis.criteria.comparison import f3a_radius, f3a_speed, f3a_length, f3a_roll_rate


@fixture
def vline():
    return ManDef(
        "vline",
        2,
        BoxLocation(Height.BTM, Direction.UPWIND, Orientation.UPRIGHT),
        Position.CENTRE,
        2,
        lambda s, r, l, p : ManDef.compile_elms(
            Loop(s, 2*r, -0.25),
            Line(s, l, 0),
            Line.from_roll(s, p, np.pi * 2),
            Line(s, l, 0),
            Loop(s, 2*r, 0.25)
        ),
        lambda elms : {
            "s": f3a_speed([e.speed for e in elms]),
            "r": f3a_radius([e.diameter for e in elms if e.__class__ is Loop]),
            "li": f3a_length([sum([e.length for e in elms[1:4]])]),
            "l": f3a_length([elms[1].length, elms[3].length]),
            "p": f3a_roll_rate([elms[2].rate])
        }
    )


def test_generator(vline):
    elms = vline.generator(50, 100, 30, 1)
    assert elms[0].diameter == 200
    assert isinstance(elms[0], Loop)



@fixture
def tophat():
    ManDef(
        "tophat",
        4,
        BoxLocation(Height.BTM, Direction.UPWIND, Orientation.UPRIGHT),
        Position.CENTRE,
        2,
        lambda s, r0, l1, p, a0, l2:
            ManDef.compile_elms(
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
    return SchedDef.parse("tests/test_inputs/p23_def.sched")

def test_parse_schedule(p23):
    
    assert p23.defs[0].name=="tophat"
    assert p23.defs[0].segments[0].radius == None
    assert p23.defs[0].segments[0].length == "l0"
    