from pytest import fixture

from flightanalysis.environment import Environment
from flightanalysis.environment.wind import WindModelBuilder
from ..conftest import flight, box
import numpy as np
import pandas as pd
from geometry import Points


@fixture
def st(flight, box):
    return State.from_flight(flight, box) 

@fixture
def wmodel():
    return WindModelBuilder.uniform(1.0, 20.0)([np.pi, 5.0])


def test_build(flight, seq, wmodel):
    env = Environment.build(flight, seq, wmodel)

    assert isinstance(env.data, pd.DataFrame)

    assert isinstance(env.wind, Points)
    assert isinstance(env[20], Environment)
    