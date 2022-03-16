from pytest import approx, fixture
from flightanalysis import Box
from flightanalysis.environment import Environment, Environments
from flightanalysis.environment.wind import WindModelBuilder
from flightanalysis.model.flow import Flow, Flows
from flightanalysis.section import Section
from pytest import approx
import numpy as np
from flightdata import Flight
from ..conftest import flight, seq

@fixture
def environments(flight, seq):
    wmodel = WindModelBuilder.uniform(1.0, 20.0)([np.pi, 1.0])
    return Environments.build(flight, seq, wmodel)


def test_build(seq, environments):
    flows = Flows.build(seq, environments)
    assert np.mean(flows.alpha) == approx(0.0, abs=1e-1)


