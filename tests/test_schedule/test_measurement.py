from flightanalysis import State
from flightanalysis.schedule.scoring import Measurement
from geometry import Point, Quaternion, Transformation, PX, PY, Euldeg, P0, Q0
from pytest import fixture
import numpy as np
from flightanalysis import Loop

@fixture
def line_tp():
    return State.from_transform(vel=PX(30)).extrapolate(2)


@fixture
def loop_tp():
    return Loop(30, 50, np.pi*3/2, 0).create_template(State.from_transform()) 


def track_setup(tp: State, cerror: Quaternion):
    cfl = tp.move(tp[0].back_transform).move(Transformation(P0(), cerror))
    return cfl.move(tp[0].transform)
    
    
def test_track_y_line(line_tp: State):
    tp = line_tp.move(Transformation(PY(100),Euldeg(0, 270, 0)))
    fl = track_setup(tp, Euldeg(0, 0, 10))

    m = Measurement.track_y(fl, tp, tp[0].transform)

    np.testing.assert_array_almost_equal(np.degrees(abs(m.value)), np.full(len(m.value), 10.0))

def test_track_y_loop(loop_tp: State):
    tp = loop_tp.move(Transformation(PY(100),Euldeg(0, 270, 0)))
    fl = track_setup(tp, Euldeg(0, 0, 10))
    m = Measurement.track_y(fl, tp, tp[0].transform)
    np.testing.assert_array_almost_equal(np.degrees(abs(m.value)), np.full(len(m.value), 0.0))