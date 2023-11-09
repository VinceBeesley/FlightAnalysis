from pytest import fixture

from flightanalysis.definition import *
from flightanalysis.elements import *
from flightanalysis.scoring import *
from flightanalysis import Manoeuvre, SchedDef
import numpy as np
from json import load



@fixture(scope="session")
def vline():
    return f3amb.create(ManInfo("Vertical Line", "vline", 2,
            Position.CENTRE,
            BoxLocation(Height.BTM, Direction.UPWIND, Orientation.UPRIGHT),
            BoxLocation(Height.BTM)
        ),
        [
            f3amb.loop(-np.pi/2),
            f3amb.roll("1/2"),
            f3amb.loop(np.pi/2),    
        ]
    )

    

@fixture(scope="session")
def man(vline):
    return vline.create(vline.info.initial_transform(170,1))

def test_create(man):
    assert isinstance(man, Manoeuvre)
    
def test_collect(vline, man):
    downgrades = vline.mps.collect(man)
    assert np.all(downgrades.speed.downgrades==0)
 

def test_to_from_dict(vline):
    
    
    vld = vline.to_dict()

    vl2 = ManDef.from_dict(vld)#


    assert isinstance(vld, dict)
    assert isinstance(vl2, ManDef)
    

    man = vl2.create(vl2.info.initial_transform(170,1))
    downgrades = vl2.mps.collect(man)

    assert np.all(downgrades.speed.downgrades==0)


@fixture
def p23_def_dict():
    with open("flightanalysis/data/p23.json", "r") as f:
        return load(f)


def test_mdef_parse_dict(p23_def_dict):
    iSp = ManDef.from_dict(p23_def_dict["trgle"])
    pass


