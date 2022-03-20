import pytest

from flightanalysis.base.constructs import Constructs

from flightanalysis.state.variables import secvars
import numpy as np


def test_subset():
    subs = secvars.subset(["time", "pos"])

    assert len(subs.data) == 2


def test_existing():
    subs = secvars.existing(["x", "y", "z"])
    assert len(subs.data) == 1

def test_missing():
    subs = secvars.missing(["x", "y", "z", "rw"])
    assert len(subs.data) == len(secvars.data) - 1


def test_contains():
    res = secvars.contains(["pos"])
    assert np.all(res==[True])

    res = secvars.contains("pos")
    assert res==True

