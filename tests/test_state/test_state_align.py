from flightanalysis import State, Manoeuvre
from flightanalysis.data.p23 import create_p23, tHat
from pytest import fixture, approx
from geometry import Transformation, Euler, P0
import numpy as np
from flightanalysis.schedule.definition import *


@fixture
def th_def() -> ManDef:
    return tHat()

@fixture
def initial_transform(th_def) -> Transformation:
    return th_def.info.initial_transform(150, 1) 

@fixture
def th(th_def: ManDef, initial_transform: Transformation) -> Manoeuvre:
    return th_def.create(initial_transform)

@fixture
def th_tp(th: Manoeuvre, initial_transform: Transformation) -> State:
    return th.create_template(initial_transform)

def test_get_manoeuvre(aligned: State, th: Manoeuvre):
    m1 = aligned.get_manoeuvre(th)
    m2 = aligned.get_manoeuvre(th.uid)
    m3 = th.get_data(aligned)

    assert len(m1.data) == len(aligned.data)
    assert len(m2.data) == len(aligned.data)
    assert len(m3.data) == len(aligned.data)

def test_get_element(aligned: State, th: Manoeuvre):
    m1 = aligned.get_element(th.elements[3])
    m2 = aligned.get_element(th.elements[3].uid)
    m3 = th.elements[3].get_data(aligned)

    assert len(m1.data) > 10
    assert len(m2.data) == len(m1.data)
    assert len(m3.data) == len(m1.data)

@fixture
def th_def_mod():
    th = tHat()
    th.mps.loop_radius.default = 100
    th.mps.line_length.default=110
    th.mps.speed.default = 20
    return th

@fixture
def th_fl(th_def_mod):
    itr = th_def_mod.info.initial_transform(150, 1)
    return th_def_mod.create(itr).create_template(itr).remove_labels()


def test_remove_labels(th_fl):
    assert not "manoeuvre" in th_fl.data.columns

@fixture
def aligned(th_tp, th_fl):
    dist, th_al = State.align(th_fl, th_tp)
    return th_al

def test_align(aligned):
    assert "manoeuvre" in aligned.data.columns

@fixture
def intended(th_def: ManDef, initial_transform: Transformation, aligned: State):
    th = th_def.create(initial_transform)
    return th.match_intention(initial_transform, aligned)[0]

def test_intended_loop_radius(intended, th_def_mod ):
    assert intended.elements[0].radius == approx(th_def_mod.mps.loop_radius.default, rel=1e-3)


