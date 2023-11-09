from flightanalysis.elements import Recovery
from geometry import Transformation, Euler, P0, PX, PY, PZ, Point
import numpy as np
from flightdata import State
from pytest import fixture, approx


@fixture
def el():
    return Recovery(30, 15, "test")

@fixture
def elt(el):
    
    att = Euler(0, np.radians(15), 0)

    return el.create_template(
        State.from_transform(Transformation(P0(), att),
        vel=att.inverse().transform_point(PX(20))
    ))



def test_create_template(el, elt):
    np.testing.assert_array_almost_equal(
        elt[-1].att.transform_point(elt[-1].vel).data, 
        PX(el.speed).data
    ) 

    assert np.arctan2(elt[-1].vel.z, elt[-1].vel.x) == approx(0)

def test_match_intention(el, elt):
    el2 = Recovery(20, 20, "test")

    el3 = el2.match_intention(Transformation(), elt)

    assert el == el3

