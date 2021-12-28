from flightanalysis.section import Section
from flightanalysis import State
from flightanalysis.flightline import FlightLine
from flightanalysis.schedule import Line
from geometry import Point, Points, Transformation
from flightdata import Fields
import numpy as np
import pandas as pd
import os
import pytest
from ..conftest import flight, box, p21, seq, aligned


def test_from_flight(flight, box):
    seq = Section.from_flight(flight, box)
    assert isinstance(seq.x, pd.Series)
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

def test_get_item(seq):
    state = seq[20]
    assert isinstance(state.pos, Point)



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


def test_existing_constructs(seq):
    exconsts = seq.existing_constructs()
    assert "pos" in exconsts
    assert not "alpha" in exconsts


def test_get_state(seq):
    st = seq.get_state_from_time(100)
    assert isinstance(st, State)


def test_align(seq, p21):
    
    flown = seq.subset(100, 493)

    template = p21.scale_distance(170.0).create_raw_template("left", 30, 170)
    
    aligned = Section.align(flown, template, 2)

    assert len(aligned[1].data) == len(flown.data) 


def test_append_columns(seq, flight):
    sec = seq.append_columns(flight.read_fields(Fields.TXCONTROLS))
    assert sec.duration == seq.duration

    assert len(sec.data) == len(seq.data)


def test_smooth_rotation():
    sec = Line(1).scale(100).create_template(Transformation(), 10, False)

    roll = sec.smooth_rotation(Point.X(1), 2 * np.pi, "body", 0.25, 0.1)

    assert np.any(pd.isna(roll.brvel)) == False


def test_from_csv():
    sec = Section.from_csv("tests/test_inputs/test_log_00000052_section.csv")
    assert isinstance(sec.gpos, Points)


def test_match_intention(aligned, p21):
    intended_p21 = p21.match_intention(aligned)

    assert not intended_p21.manoeuvres[0].elements[2].diameter == intended_p21.manoeuvres[0].elements[3].diameter


