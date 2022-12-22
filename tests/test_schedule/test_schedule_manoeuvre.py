import numpy as np
import pandas as pd

from flightanalysis.schedule import Manoeuvre, Schedule
from flightanalysis.state import State

from flightanalysis.schedule.elements import Line, Loop
from geometry import Point, Quaternion, Transformation, Coord

from pytest import fixture
from flightanalysis.data.p23 import *



@fixture(scope="session")
def tophat():
    return tHat().create()



def test_create_template(tophat: Manoeuvre):
    template = tophat.create_template()

    assert isinstance(template, State)

    
def test_get_elm_by_type(v8):
    lines = v8.get_elm_by_type(Line)
    assert len(lines) == 3
    lines_loops = v8.get_elm_by_type([Line, Loop])
    assert len(lines_loops) == 5

def test_replace_elms(v8):
    elms = [elm.set_parms(length=10) for elm in v8.elements[:2]]
    new_v8 = v8.replace_elms(elms)
    assert new_v8.elements[0].uid == elms[0].uid
    assert new_v8.elements[0].length == 10

def test_fix_loop_diameters(v8):
    new_v8 = v8.replace_elms([v8.elements[3].set_parms(diameter=10.0)])
    fixed_v8 = new_v8.fix_loop_diameters()
    assert fixed_v8.elements[3].diameter == np.mean([0.45, 10])

def test_get_bounded_lines(v8, sql):
    assert v8.get_bounded_lines() == []
    sql_lines = sql.get_bounded_lines()
    assert len(sql_lines) == 4
    assert len(sql_lines[0]) == 1
    assert len(sql_lines[1]) == 3
    assert len(sql_lines[2]) == 1
    assert len(sql_lines[3]) == 3
    

def test_get_id_for_element(v8):
    assert v8.get_id_for_element(v8.elements[3])[0] == 3

    np.testing.assert_array_equal(
        v8.get_id_for_element(v8.elements[3:5]),
        [3, 4]
    )

def test_df(v8):
    assert isinstance(Manoeuvre.create_elm_df(v8.elements), pd.DataFrame)

def test_set_bounded_line_length():
    
    bline = [Line(50.0, 0.0, True), Line(10.0, 1.0, True), Line(100.0, 0.0, True)]

    nbline = Manoeuvre.set_bounded_line_length(bline, 100.0)
    assert Manoeuvre.calc_line_length(nbline) == 100.0

def test_filter_elms_by_attribute(v8):
    lmats = Manoeuvre.filter_elms_by_attribute(v8.elements, r_tag=True)
    assert len(lmats) == 2


def test_get_data(sql, aligned):
    sql_data = sql.get_data(aligned)

    assert sql_data.duration <= aligned.duration
    
    assert np.all(sql_data.data.manoeuvre == sql.uid)

def test_get_subset(sql, aligned):
    sql_data = sql.get_data(aligned)
    elm_data = sql.get_subset(aligned, 3, 5)
    assert sql_data.duration >= elm_data.duration


