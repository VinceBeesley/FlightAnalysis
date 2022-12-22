from flightanalysis.schedule.elements import Spin
from geometry import Transformation, Point, Quaternion, PZ, PX
import numpy as np
import pandas as pd
from pytest import fixture, approx

@fixture
def spin():
    return Spin(30.0, -1)

@fixture
def nose_drop(spin):
    return spin._create_nose_drop(Transformation())

def test_create_nose_drop(spin, nose_drop):
    assert Point.angle_between(
        nose_drop[-1].att.transform_point(PX()),
        PZ(-1)
    )[0] == approx(spin.break_angle)

@fixture
def autorotation(spin, nose_drop):
    return spin._create_autorotation(nose_drop[-1].transform)

def test_create_autorotation(spin, autorotation):
    np.testing.assert_allclose(
        Point.angle_between(autorotation.vel, PX(30.0)),
        spin.break_angle
    )


def test_create_template(spin):
    template = spin.create_template(Transformation())

    assert np.any(pd.isna(template.rvel)) == False
    assert template[-1].pos.z < 0

    assert template[-1].att.transform_point(Point(0,0,1)).x== approx(1)

