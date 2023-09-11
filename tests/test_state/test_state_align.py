from flightanalysis import State, Manoeuvre, SchedDef
from pytest import fixture, approx
from geometry import Transformation, Euler, P0
import numpy as np
from flightanalysis.schedule.definition import *


@fixture
def th_def() -> ManDef:
    return SchedDef.from_dict("p23")[0]

@fixture
def initial_transform(th_def) -> Transformation:
    return th_def.info.initial_transform(150, 1) 

@fixture
def th(th_def: ManDef, initial_transform: Transformation) -> Manoeuvre:
    return th_def.create(initial_transform)

@fixture
def th_tp(th: Manoeuvre, initial_transform: Transformation) -> State:
    return th.create_template(initial_transform)

@fixture
def th_def_mod(th_def) -> ManDef:
    th = th_def
    th.mps.loop_radius.default = 100
    th.mps.line_length.default=110
    th.mps.speed.default = 20
    return th

@fixture
def th_fl(th_def_mod) -> State:
    itr = th_def_mod.info.initial_transform(150, 1)
    return th_def_mod.create(itr).create_template(itr).remove_labels()

@fixture
def aligned(th_tp, th_fl) -> State:
    dist, th_al = State.align(th_fl, th_tp)
    return th_al


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



def test_remove_labels(th_fl):
    assert not "manoeuvre" in th_fl.data.columns


def test_align(aligned):
    assert "manoeuvre" in aligned.data.columns

@fixture
def intended(th_def: ManDef, initial_transform: Transformation, aligned: State) -> Manoeuvre:
    th = th_def.create(initial_transform)
    return th.match_intention(initial_transform, aligned)[0]

def test_intended_loop_radius(intended, th_def_mod):
    assert intended.elements[0].radius == approx(th_def_mod.mps.loop_radius.default, rel=1e-3)



def test_copy_labels(th_tp):
    th_fl = th_tp.remove_labels()
    th_al = State.copy_labels(th_tp, th_fl)

    assert "element" in th_al.data.columns

def test_subset(aligned):
    els = aligned.data.element.unique()[:3]

    al_ss = aligned.get_subset(els, col="element")
    assert all([e in els for e in al_ss.data.element.unique()])

    al_ss = aligned.get_subset(slice(0,3,None), col="element")
    assert all([e in els for e in al_ss.data.element.unique()])

    al_ss = aligned.get_subset(2, "element")
    assert al_ss.data.element.unique()[0] == els[2]


from geometry import PX
from flightanalysis.base.table import Time

def test_copy_labels_min_len():
    tp = State.from_transform(Transformation(), vel=PX(30)) \
        .fill(Time.from_t(np.linspace(0, 1, 10))) \
            .label(
                element=list('aaaabbbccc'),
                manoeuvre=list('mmmmnnnnnn')
            )
    
    path = [[i, i] for i in range(10)]
    path[4] = [3,4]
    path[5] = [3,5]
    path[6] = [3,6]

    al = State.copy_labels(tp, tp.remove_labels(), path, 2)
    assert len(al.get_element('b')) >=2
    pass

    