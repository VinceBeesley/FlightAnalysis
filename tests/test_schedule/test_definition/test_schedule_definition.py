from pytest import fixture

from flightanalysis.schedule.definition.definition import *
from flightanalysis.schedule.elements import *
from flightanalysis.criteria.comparison import *

@fixture(scope="session")
def vline():
    md = ManDef(
        "vline",
        ManParms.from_list([
            ManParm("s", f3a_speed, 30, []),
            ManParm("r", f3a_radius, 100, []), 
            ManParm("l", f3a_length, 100, []), 
            ManParm("rate", f3a_roll_rate, 1, []),
            ManParm("d", HardZero(10, 1), 1, []),
            ManParm("p", f3a_length, 5, [])
        ])
    )

    p1 = md.add_loop("e1", "s", "r", -np.pi/2, 0)
    p2 = md.add_roll_centred("e2", "s", "l", "rate", "d", "p", [np.pi/2, -np.pi/2], f3a_length)
    p3=md.add_loop("e3", "s", "r", np.pi/2, 0)
    
    md.mps.append_collectors(dict(
        s=[p["speed"] for p in [p1,p2,p3]],
        r=[p["radius"] for p in [p1, p3]],
        l=p2["length"],
        rate=p2["rate"],
        d=p2["direction"],
        p=p2["pause"]
    ))

    return md


@fixture(scope="session")
def man(vline):
    return vline.create()

def test_create(man):
    assert isinstance(man, Manoeuvre)
    
def test_collect(vline, man):
    downgrades = vline.mps.collect(man)
    assert np.all(np.array(downgrades["s"])==0)
 

