import numpy as np
import pandas as pd

from flightanalysis.schedule import Manoeuvre, Schedule
from flightanalysis.state import State

from flightanalysis.schedule.elements import Line, Loop
from geometry import Point, Quaternion, Transformation, Coord

from pytest import fixture
from flightanalysis.data import get_schedule_definition



@fixture(scope="session")
def th_def():
    return get_schedule_definition("p23")[0]

@fixture(scope="session")
def itrans(th_def):
    return th_def.info.initial_transform(170, 1)

@fixture(scope="session")
def tophat(th_def, itrans):
    return th_def.create(itrans)


def test_create_template(tophat: Manoeuvre, itrans):
    template = tophat.create_template(itrans)

    assert isinstance(template, State)
