from flightanalysis.state import State
from flightanalysis.flightline import FlightLine
from flightanalysis.schedule import Line
from geometry import Point, Points, Transformation
from flightdata import Fields
import numpy as np
import pandas as pd
import os
from ..conftest import flight, box, p21, seq, aligned
from pytest import approx


def test_to_csv(seq):
    csv_file = seq.to_csv('tests/test.csv')
    seq2 = State.from_csv(csv_file) 
    assert seq.duration == seq2.duration
    os.remove(csv_file)


def test_body_to_world(flight):

    seq = State.from_flight(
        flight, FlightLine.from_initial_position(flight))

    pnew = seq.body_to_world(Point(1, 0, 0))

    assert isinstance(pnew, Point)



def test_get_state(seq):
    st = seq[100]
    assert isinstance(st, State)


def test_align(seq, p21):
    
    flown = seq[100:493]

    template = p21.scale_distance(170.0).create_raw_template("left", 30, 170)
    
    aligned = State.align(flown, template, 2)

    assert len(aligned[1].data) == len(flown.data) 


def test_append_columns(seq, flight):
    sec = seq.append_columns(flight.read_fields(Fields.TXCONTROLS))
    assert sec.duration == seq.duration

    assert len(sec.data) == len(seq.data)


def test_smooth_rotation():
    sec = Line(1).scale(100).create_template(Transformation(), 10, False)

    roll = sec.smooth_rotation(Point.X(1), 2 * np.pi, "body", 0.25, 0.1)

    assert np.any(pd.isna(roll.brvel)) == False



def test_match_intention(aligned, p21):
    intended_p21 = p21.match_intention(aligned)

    assert not intended_p21.manoeuvres[0].elements[2].diameter == intended_p21.manoeuvres[0].elements[3].diameter


