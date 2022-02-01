from flightanalysis import State
from flightanalysis.flightline import Box, FlightLine
import unittest
from geometry import Point, Quaternion
from flightdata import Flight, Fields
import numpy as np
import pandas as pd
import pytest

flight = Flight.from_csv('tests/test_inputs/test_log_00000052_flight.csv')


def test_missing_vars():
    with pytest.raises(AssertionError) as einfo:
        st = State(dict())


def test_from_constructs():
    st = State.from_constructs(time=5, pos=Point.zeros(), att=Quaternion.from_euler(Point.zeros()))
    assert st.transform.translation == Point.zeros()
