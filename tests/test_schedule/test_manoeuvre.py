import numpy as np
import pandas as pd
import unittest
from flightanalysis.schedule import Manoeuvre, Schedule
from flightanalysis import get_schedule, Section
from flightanalysis.schedule.elements import Line, Loop, rollmaker
from geometry import Point, Quaternion, Transformation, Coord

import pytest



@pytest.fixture(scope="session")
def schedule() -> Schedule:
    return get_schedule("F3A", "P21")


@pytest.fixture(scope="session")
def v8(schedule) -> Manoeuvre:
    return schedule.manoeuvres[0]

@pytest.fixture(scope="session")
def sql(schedule) -> Manoeuvre:
    return schedule.manoeuvres[2]


@pytest.fixture(scope="session")
def aligned():
    return Section.from_csv("tests/test_inputs/test_log_00000052_aligned.csv")

def test_create_template(v8: Manoeuvre):
    v8_template = v8.scale(100).create_template(
        Transformation.from_coords(
            Coord.from_nothing(), Coord.from_nothing()),
        30.0
    )

    np.testing.assert_array_almost_equal(
        v8_template.get_state_from_index(-1).pos.to_list(),
        [120, 0.0, 0.0]
    )

    
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


