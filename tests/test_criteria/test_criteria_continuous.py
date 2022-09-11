from pytest import fixture
import numpy as np
import pandas as pd
from flightanalysis.criteria import *


@fixture
def lsdata():
    return pd.read_csv("tests/test_criteria/example_loop_scoring_data.csv")


def test_continuous(lsdata):
    res = intra_f3a_angle("trial", lsdata.track)

    assert len(res.errors) == 2
    
    dgs = np.trunc(intra_f3a_angle.lookup(res.errors) * 2) / 2

    np.testing.assert_array_equal(
         dgs,
         res.downgrades 
    )
    np.testing.assert_array_equal(
        res.carry_over,
        intra_f3a_angle.lookup(res.errors) % 0.50
    ) 

