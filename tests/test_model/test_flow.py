from pytest import approx, fixture
from flightanalysis.flightline import Box
from flightanalysis.environment import Environment
from flightanalysis.environment.wind import WindModelBuilder
from flightanalysis.model.flow import Flow
from flightanalysis.state import State
from pytest import approx
import numpy as np
from flightdata import Flight
from ..conftest import flight, box, st

@fixture
def environments(flight, st):
    wmodel = WindModelBuilder.uniform(1.0, 20.0)([np.pi, 1.0])
    return Environment.build(flight, st, wmodel)


def test_build(st, environments):
    flows = Flow.build(st, environments)
    assert np.mean(flows.alpha) == approx(0.0, abs=1e-1)


