
from flightanalysis.schedule.elements import Snap
from pytest import fixture, approx
from geometry import Transformation, PX, Point
import numpy as np



@fixture
def single_snap():
    return Snap(30.0, 1.0, 3.0)



def test_create_break(single_snap):
    brk = single_snap._create_break(Transformation())

    assert Point.angle_between(
        brk[-1].att.transform_point(PX()), 
        PX()
    )[0] == approx(single_snap.break_angle * single_snap.direction)

    assert Point.angle_between(brk[-1].vel, PX(30.0)) == approx(single_snap.break_angle * single_snap.direction)


def test_create_autorotation(single_snap):
    auto = single_snap._create_autorotation(Transformation())

    np.testing.assert_allclose(
        Point.angle_between(auto.vel, PX(30.0)),
        single_snap.break_angle * single_snap.direction
    )



