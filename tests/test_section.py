from flightanalysis.section import Section
from flightanalysis.state import State
from flightanalysis.flightline import Box, FlightLine
from flightanalysis.schedule import Schedule, Categories, get_schedule

import unittest
from geometry import Point, Quaternion, Points, Quaternions, GPSPosition
from flightdata import Flight, Fields
import numpy as np
import pandas as pd
from io import open
from json import load
import os
import pytest


@pytest.fixture(scope="session")
def flight():
    return Flight.from_csv('tests/test_inputs/test_log_00000052_flight.csv')

@pytest.fixture(scope="session")
def box():
    return Box.from_json('tests/test_inputs/test_log_box.json')

@pytest.fixture(scope="session")
def p21():
    return get_schedule(Categories.F3A, "P21")

@pytest.fixture(scope="session")
def seq(flight, box): 
    return Section.from_flight(flight, box)

def test_from_flight(flight, box):
    seq = Section.from_flight(flight, box)
    assert isinstance(seq.x, pd.Series)
    assert isinstance(seq.y, pd.Series)
    assert isinstance(seq.z, pd.Series)
    assert isinstance(seq.rw, pd.Series)
    assert isinstance(seq.rx, pd.Series)
    assert isinstance(seq.ry, pd.Series)
    assert isinstance(seq.rz, pd.Series)
    assert seq.z.mean() > 0
    np.testing.assert_array_less(np.abs(seq.pos.to_numpy()[0]), 50.0 )


def test_to_csv(seq):
    csv_file = seq.to_csv('tests/test.csv')
    seq2 = Section.from_csv(csv_file) 
    assert seq.duration == seq2.duration
    os.remove(csv_file)

def test_generate_state(seq):
    state = seq.get_state_from_index(20)
    assert isinstance(state.pos, Point)

def test_from_line():
    """from inverted at 30 m/s, fly in a stright line for 1 second
    """
    initial = State(
        Point(60, 170, 150),
        Quaternion.from_euler(Point(np.pi, 0, np.pi)),
        Point(30, 0, 0)
    )  # somthing like the starting pos for a P21 from the right

    line = Section.from_line(
        initial.transform,
        10,
        100
    )
    np.testing.assert_array_almost_equal(
        line.pos.iloc[-1], [-40, 170, 150]
    )
    np.testing.assert_array_almost_equal(
        line.bvel, np.tile(np.array([10, 0, 0]), (len(line.data.index), 1))
    )
    np.testing.assert_array_almost_equal(
        line.att, np.tile(
            list(Quaternion.from_euler(Point(np.pi, 0, np.pi))),
            (len(line.data.index), 1))
    )


def test_from_loop():
    """do the outside loop at the start of the P sequence"""
    initial = State(
        Point(0, 170, 150),
        Quaternion.from_euler(Point(np.pi, 0, np.pi)),
        Point(10 * np.pi, 0, 0),  # 620 m in 10 seconds
        Point(0, np.pi / 5, 0)
    )

    radius = Section.from_loop(initial.transform, 10*np.pi, 1, 50)
    np.testing.assert_array_almost_equal(
        list(radius.get_state_from_index(-1).pos),
        list(Point(0, 170, 150))
    )

def test_body_to_world(flight):

    seq = Section.from_flight(
        flight, FlightLine.from_initial_position(flight))

    pnew = seq.body_to_world(Point(1, 0, 0))

    assert isinstance(pnew, Points)

def test_subset(flight):
    seq = Section.from_flight(
        flight, FlightLine.from_initial_position(flight))

    assert isinstance(seq.subset(100, 200), Section)
    pytest.approx(seq.subset(100, 200).data.index[-1], 200, 0)

    pytest.approx(seq.subset(-1, 200).data.index[-1], 200, 0)

    pytest.approx(
        seq.subset(-1, -1).data.index[-1],
        seq.data.index[-1],
        2
    )

def test_get_state(seq):
    st = seq.get_state_from_time(100)
    assert isinstance(st, State)

def test_stack():
    initial = State(
        Point(10 * np.pi, 170, 150),
        Quaternion.from_euler(Point(np.pi, 0, np.pi)),
        Point(10 * np.pi, 0, 0),
        Point(np.pi, 0, 0)
    )

    line = Section.from_line(initial.transform, 30, 20)

    last_state = line.get_state_from_index(-1)
    
    radius = Section.from_loop(last_state.transform, 30, 1, 50)

    combo = Section.stack([line, radius])

    assert len(combo.data) == len(line.data) + len(radius.data) - 1
    assert combo.data.iloc[-1].bvx == 30

    assert isinstance(combo.get_state_from_time(10), State)

    assert radius.data.index[-1] + line.data.index[-1] == combo.data.index[-1]

    assert combo.get_state_from_time(0.0).pos == combo.get_state_from_index(0).pos

    assert combo.data.index.name == "time_index"

def test_align(seq, p21):
    
    flown = seq.subset(100, 493)

    template = p21.scale_distance(170.0).create_raw_template("left", 30, 170)
    
    aligned = Section.align(flown, template, 2)

    assert len(aligned[1].data) == len(flown.data) 

