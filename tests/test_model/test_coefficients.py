from pytest import approx, fixture
from flightanalysis.environment import Environments
from flightanalysis.environment.wind import WindModelBuilder
from flightanalysis.model.flow import Flows
from pytest import approx
import numpy as np
from ..conftest import flight, seq
from flightanalysis.model.constants import cold_draft
from flightanalysis.model.coefficients import Coefficients


@fixture
def environments(flight, seq):
    wmodel = WindModelBuilder.uniform(1.0, 20.0)([np.pi, 1.0])
    return Environments.build(flight, seq, wmodel)

@fixture
def flows(seq, environments):
    return Flows.build(seq, environments)

def test_build(seq, flows):
    flows = Coefficients.build(seq, flows, cold_draft)

    pass


