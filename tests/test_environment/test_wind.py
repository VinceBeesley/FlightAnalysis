from flightanalysis.environment.wind import wind_power_law_builder, wind_fit_builder, get_wind_error, uniform_wind_builder
import pytest
import numpy as np 
import pandas as pd
from geometry import Points, Point
from ..conftest import seq



def test_wind_power_law_builder():
    pl = wind_power_law_builder([0.0, 5.0, 0.2])

    assert pl(300, 0.0).x==5
    assert isinstance(pl(300, 0.0), Point)

    pl_res = pl(np.random.random(100), np.random.random(100))
    assert isinstance(pl_res, Points)
    assert pl_res.count, 100


def test_wind_fit_builder():
    pl = wind_fit_builder(np.random.random(20))
    assert isinstance(pl(300, 0.0), Point)

    pl_res = pl(np.random.random(100), np.random.random(100))
    assert isinstance(pl_res, Points)
    assert pl_res.count, 100


def test_get_wind_error(seq):
    body_axis = seq.flying_only()
    judging_axis = body_axis.to_judging()
    error = get_wind_error([0.0, 3.0, 0.2], wind_power_law_builder, body_axis, judging_axis)

    assert isinstance(error, float)

    error2 = get_wind_error([0.0, 20.0, 0.2], wind_power_law_builder, body_axis, judging_axis)

    assert error2 > error

from flightanalysis import Line
from geometry import Transformation


def test_wind_error_2():
    sec = Line(100).create_template(Transformation(), 30.0)
    wind = sec.judging_to_wind(Points.Y(np.full(len(sec.data), 10.0)))

    err = get_wind_error([0.0, 10.0], uniform_wind_builder, wind, sec)
    assert err == 0.0