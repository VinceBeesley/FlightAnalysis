from pytest import fixture
import numpy as np
from flightanalysis.schedule.definition import ElDef, ElDefs, _a
from flightanalysis.schedule.elements import Loop
from flightanalysis.schedule.definition import ManParm, ManParms

@fixture
def mps():
    return ManParms.create_defaults_f3a()


@fixture
def loopdef(mps):
    return ElDef.loop(
        "test", 
        False,  
        mps.speed, 
        mps.loop_radius,  
        np.pi/2,
        0)
    

def test_call(loopdef, mps):
    loop = loopdef(mps)

    assert loop.radius == mps.loop_radius.default


@fixture
def eds(mps):
    return ElDefs([
        ElDef.line("e1", 2*mps.speed, mps.line_length - mps.loop_radius, 0),
        ElDef.line("e2", mps.speed, 30, 0),
        ElDef.loop("e3", False, mps.speed, 40, np.pi/2, 0)
    ])


def test_builder_list(eds, mps):
    bl = eds.builder_list("length")
    assert len(bl) == 2
    assert _a(bl[0])(mps) == 130 - 55
    assert _a(bl[1])(mps) == mps.speed.default


