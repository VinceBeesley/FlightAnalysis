import pytest
from flightanalysis.environment import Environment, Environments
from flightanalysis.environment.wind import WindModelBuilder
from ..conftest import flight, seq
import numpy as np
import pandas as pd
from geometry import Points

@pytest.fixture
def wmodel():
    return WindModelBuilder.uniform(1.0, 20.0)([np.pi, 5.0])


def test_build(flight, seq, wmodel):
    env = Environments.build(flight, seq, wmodel)

    assert isinstance(env.data, pd.DataFrame)

    assert isinstance(env.gwind, Points)
    assert isinstance(env[20], Environment)
    