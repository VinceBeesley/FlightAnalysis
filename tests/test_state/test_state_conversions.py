import numpy as np
from flightanalysis.state import State

from pytest import approx, fixture
from flightanalysis.schedule.elements.line import Line
from flightanalysis import State
from geometry import Points, Transformation, Point, P0, Euler, PY
from ..conftest import st, flight, box
from flightanalysis.environment import Environment
from flightanalysis.model.flow import Flow

def test_to_judging(st: State):
    
    jst = st.to_judging()

    assert isinstance(jst, State)

    env = Environment.from_constructs(st.time)
    flw_body = Flow.build(st, env)
    flw_judge = Flow.build(jst, env)

    
    #this wont reduce alpha and beta to zero as velocity comes from IMU,
    #but should be order of magnitude smaller
    assert np.nanmean(np.abs(flw_body.alpha / flw_judge.alpha)) > 1000
    assert np.nanmean(np.abs(flw_body.beta / flw_judge.beta)) > 1000


@fixture
def sl_wind_axis():
    return Line(30, 100, 0).create_template(
        State.from_transform(Transformation(P0(), Euler(0, np.pi, 0)))
    )

def test_to_judging_sim(sl_wind_axis):
    body_axis = sl_wind_axis.superimpose_angles(Point(0, np.radians(20), 0))  
    env = Environment.from_constructs(sl_wind_axis.time)
    
    judging = body_axis.to_judging()
    assert judging.pos == sl_wind_axis.pos
    np.testing.assert_almost_equal(sl_wind_axis.att.data, judging.att.data)

    np.testing.assert_almost_equal(
        judging.vel.data,
        Point(30,0,0).tile(len(judging)).data
    )

def test_judging_to_wind(sl_wind_axis):
    judge_axis = sl_wind_axis
    wind_axis = judge_axis.convert_state(Point(0, 0, np.radians(10)))
    body_axis = wind_axis.convert_state(Point(0, np.radians(20), 0))  

    env = Environment.from_constructs(
        sl_wind_axis.time, 
        wind=PY(30*np.tan(np.radians(10)), len(sl_wind_axis))
    )

    wind = judge_axis.judging_to_wind(env)

    np.testing.assert_array_almost_equal(wind.att.data, wind_axis.att.data)



