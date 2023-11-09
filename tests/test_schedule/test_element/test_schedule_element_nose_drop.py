from flightanalysis.elements import NoseDrop
from geometry import Transformation, Euler, P0, PX, PY, PZ, Point
import numpy as np
from flightdata import State
from pytest import fixture


@fixture
def nd():
    return NoseDrop(10, 15, np.radians(45), np.radians(90))

@fixture
def ndt(nd):
    
    att = Euler(0, np.radians(-20), 0)

    return nd.create_template(State.from_transform(
        Transformation(P0(), att),
        vel=att.inverse().transform_point(PX(30))
    ))



def test_create_template(nd, ndt):
    np.testing.assert_array_almost_equal(
        ndt[-1].att.transform_point(ndt[-1].vel).data, 
        PZ(-nd.speed).data
    ) 


def test_match_intention(nd, ndt):
    nd2 = NoseDrop(15,30,np.radians(25), nd.uid)


    nd3 = nd2.match_intention(Transformation(), ndt)

    assert nd==nd3
