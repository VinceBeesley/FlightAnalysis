import numpy as np
from flightanalysis.state import State

from pytest import approx, fixture
from flightanalysis.schedule.elements.line import Line
from flightanalysis.state.tools.conversions import to_judging, body_to_wind
from geometry import Points, Transformation, Point, P0, Euler
from ..conftest import st, flight, box
from flightanalysis.environment import Environment
from flightanalysis.model.flow import Flow

def test_to_judging(st: State):
    
    jst = to_judging(st)

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
    return Line(100, 0).create_template(
        Transformation(P0(), Euler(0, np.pi, 0)), 
        30
    )

def test_to_judging_sim(sl_wind_axis):
    body_axis = sl_wind_axis.superimpose_angles(Point(0, np.radians(20), 0))  
    env = Environment.from_constructs(sl_wind_axis.time)
    
    judging = to_judging(body_axis)
    assert judging.pos == sl_wind_axis.pos
    np.testing.assert_almost_equal(sl_wind_axis.att.data, judging.att.data)

    np.testing.assert_almost_equal(
        judging.vel.data,
        Point(30,0,0).tile(len(judging)).data
    )




def test_body_to_wind(st: State):
    
    alpha, beta = st.measure_aoa()

    wst = body_to_wind(st, alpha, beta)
    
    jst = to_judging(st)

    np.testing.assert_array_almost_equal(wst.att.data, jst.att.data, 0)



def test_judging_to_wind():
    judging = Line(100.0).create_template(Transformation(), 20.0)
    wind_vec = Points.Y(np.full(len(judging.data), 5.0))
    wind = judging.judging_to_wind(wind_vec)

    alpha, beta = wind.measure_aoa()
    assert beta[20] == approx(np.arctan(5/20))


