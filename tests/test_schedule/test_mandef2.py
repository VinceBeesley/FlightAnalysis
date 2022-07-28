from pytest import fixture

from flightanalysis.schedule.definition import *
from flightanalysis.schedule.elements import *
from flightanalysis.criteria.comparison import *


@fixture
def vline():


    els = ElDefs.from_list([
        ElDef("e1", Loop, dict(
            speed=lambda mp: mp.s,
            diameter=lambda mp: 2 * mp.r,
            angle=-np.pi/2,
            roll=0
        )),
        ElDef("e2", Line, dict(
            speed=lambda mp: mp.s,
            length=lambda mp: 0.5 * mp.l - mp.p * np.pi * mp.s,
            roll=0
        )),
        ElDef("e3", Line, dict(
            speed=lambda mp: mp.s,
            length=lambda mp: 2 * mp.p * np.pi * mp.s,
            roll=lambda mp: 2 * mp.p * mp.direction
        )),
        ElDef("e4", Line, dict(
            speed=lambda mp: mp.s,
            length=lambda mp: 0.5 * mp.l - mp.p * np.pi * mp.s,
            roll=0
        )),
        ElDef("e5", Loop, dict(
            speed=lambda mp: mp.s,
            diameter=lambda mp: 2 * mp.r,
            angle=-np.pi/2,
            roll=0
        ))
    ])

    parms = ManParms.from_list([
        ManParm("s", f3a_speed, 30, lambda es: [e.speed for e in es]),
        ManParm("r", f3a_radius, 100, lambda es: [e.diameter / 2 for e in es if e.__class__ is Loop]), 
        ManParm("l", f3a_length, 100, lambda es: [es.e2.length + es.e3.length + es.e4.length]), 
        ManParm("l1", f3a_length, None, lambda es: [es.e2.length, es.e4.length]),  # this is checked but driven by l, p and s?
        ManParm("p", f3a_roll_rate, 100, lambda es: [es.e3.rate]), 
        ManParm("d", f3a_free, 1, lambda es: [es.e3.direction]), 
    ])


    return ManDef("vline", parms,els)

def test_vline(vline):
    pass