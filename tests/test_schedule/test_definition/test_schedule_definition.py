from pytest import fixture

from flightanalysis.schedule.definition import *
from flightanalysis.schedule.elements import *
from flightanalysis.criteria.comparison import *
from flightanalysis import Manoeuvre


import dill as pickle


@fixture(scope="session")
def vline():
    md = ManDef(ManInfo(
            "Vertical Line", 
            "vline", 
            2,
            Position.CENTRE,
            BoxLocation(Height.BTM, Direction.UPWIND, Orientation.UPRIGHT),
            BoxLocation(Height.BTM)
    ))

    p1 = md.add_loop(-np.pi/2)
    p2 = md.add_simple_roll("1/2")
    p3=md.add_loop(np.pi/2)
    
    return md


@fixture(scope="session")
def man(vline):
    return vline.create(vline.info.initial_transform(170,1))

def test_create(man):
    assert isinstance(man, Manoeuvre)
    
def test_collect(vline, man):
    downgrades = vline.mps.collect(man)
    assert np.all(np.array(downgrades["speed"])==0)
 

def test_pickle(vline, man):
    
    vlpk = pickle.dumps(vline)
    
    vline2 = pickle.loads(vlpk)
    downgrades = vline2.mps.collect(man)
    assert np.all(np.array(downgrades["speed"])==0)