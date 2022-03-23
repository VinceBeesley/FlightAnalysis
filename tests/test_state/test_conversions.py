import numpy as np
from flightanalysis.state import State

from pytest import approx
from flightanalysis.schedule.elements.line import Line
from flightanalysis.state.tools.conversions import to_judging, body_to_wind
from geometry import Points, Transformation, Point

def test_to_judging(seq: State):
    sec = seq.flying_only()
    jsec = to_judging(sec)

    assert isinstance(jsec, State)

    aold, bold = sec.measure_aoa()
    anew, bnew = jsec.measure_aoa()

    #this wont reduce alpha and beta to zero as original velocity was direct from IMU,
    #new is calculated, but should be order of magnitude smaller
    assert np.mean(np.abs(aold / anew)) > 30
    assert np.mean(np.abs(bold / bnew)) > 30

def test_body_to_wind(seq: State):
    sec = seq.flying_only()
    alpha, beta = sec.measure_aoa()

    wsec = body_to_wind(sec, alpha, beta)
    
    jsec = to_judging(sec)

    np.testing.assert_array_almost_equal(wsec.gatt.data, jsec.gatt.data, 0)



def test_judging_to_wind():
    judging = Line(100.0).create_template(Transformation(), 20.0)
    wind_vec = Points.Y(np.full(len(judging.data), 5.0))
    wind = judging.judging_to_wind(wind_vec)

    alpha, beta = wind.measure_aoa()
    assert beta[20] == approx(np.arctan(5/20))


