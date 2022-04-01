import pytest
from flightanalysis.controls import Controls, cold_draft_controls, Surfaces
from flightdata import Flight
import numpy as np
import pandas as pd

@pytest.fixture
def flight():
    return Flight.from_csv("tests/test_inputs/test_log_00000052_flight.csv")


def test_init(flight):
    cont = Controls.build(flight, cold_draft_controls)

    assert isinstance(cont.surfaces, Surfaces)
    


