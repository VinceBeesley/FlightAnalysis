import numpy as np
import pandas as pd

from flightanalysis import Manoeuvre, Schedule, State, SchedDef, Line, Loop
from geometry import Point, Quaternion, Transformation, Coord

from pytest import fixture


@fixture(scope="session")
def th_def():
    return SchedDef.load("p23")[0]

@fixture(scope="session")
def itrans(th_def):
    return th_def.info.initial_transform(170, 1)

@fixture(scope="session")
def tophat(th_def, itrans):
    return th_def.create(itrans)


def test_create_template(tophat: Manoeuvre, itrans):
    template = tophat.create_template(itrans)

    assert isinstance(template, State)
