from flightanalysis import State
from flightanalysis.flightline import Box, FlightLine
import unittest
from geometry import Point, Quaternion, Transformation
from flightdata import Flight, Fields
import numpy as np
import pandas as pd
import pytest

flight = Flight.from_csv('tests/test_inputs/test_log_00000052_flight.csv')



def test_from_constructs():
    st = State.from_constructs(time=5, pos=Point.zeros(), att=Quaternion.from_euler(Point.zeros()))
    assert st.transform.translation == Point.zeros()

def test_from_transform():
    st =State.from_transform(Transformation(),bvel=Point(30, 0, 0))
    assert st.bvel.x == 30


    