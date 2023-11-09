from flightanalysis.elements import PitchBreak
from geometry import Transformation, Euler, P0, PX, PY, PZ, Point
import numpy as np
from flightdata import State
from pytest import fixture


@fixture
def pb():
    return PitchBreak(30, 15, np.radians(20), "test")

@fixture
def pbt(pb):
    
    att = Euler(0, np.radians(15), 0)

    return pb.create_template(
        State.from_transform(Transformation(P0(), att),
        vel=att.inverse().transform_point(PX(20))
    ))



def test_create_template(pb, pbt):
    np.testing.assert_array_almost_equal(
        pbt[-1].att.transform_point(pbt[-1].vel).data, 
        PX(pb.speed).data
    ) 



def test_match_intention(pb, pbt):
    pb2 = PitchBreak(20, 20, -np.radians(30), "test")

    pb3 = pb2.match_intention(Transformation(), pbt)

    assert pb3 == pb


#def test_match_intention(nd, ndt):
#    nd2 = NoseDrop(15,30,np.radians(25), nd.uid)
#
#
#    nd3 = nd2.match_intention(Transformation(), ndt)
#
#    assert nd==nd3
