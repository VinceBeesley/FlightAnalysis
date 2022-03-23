from pytest import approx, fixture
from flightanalysis.environment import Environment
from flightanalysis.environment.wind import WindModelBuilder
from flightanalysis.model.flow import Flow
from pytest import approx
import numpy as np
from ..conftest import flight, box
from flightanalysis.model.constants import cold_draft
from flightanalysis.model.coefficients import Coefficients
from flightanalysis.state import State

@fixture
def st(flight, box):
    return State.from_flight(flight, box)


@fixture
def environments(flight, seq):
    wmodel = WindModelBuilder.uniform(1.0, 20.0)([np.pi, 1.0])
    return Environment.build(flight, seq, wmodel)

@fixture
def flows(seq, environments):
    return Flow.build(seq, environments)

def test_build(seq, flows):
    flows = Coefficients.build(seq, flows, cold_draft)

    pass


