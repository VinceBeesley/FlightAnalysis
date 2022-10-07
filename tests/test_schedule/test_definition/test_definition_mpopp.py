from pytest import fixture

from flightanalysis.schedule.definition.manoeuvre_parameters import *


@fixture
def mps():
    return ManParms.create_defaults_f3a()


def test_mp_opp_mp(mps):
    mpopp = mps.loop_radius + mps.line_length

    assert isinstance(mpopp, MPOpp)

    assert str(mpopp) == "(loop_radius+line_length)"

    assert mpopp(mps) == mps.loop_radius.value + mps.line_length.value

def test_mp_opp_mpopp(mps):
    mpopp = mps.loop_radius + mps.line_length * mps.loop_radius

    assert str(mpopp) == "(loop_radius+(line_length*loop_radius))"

    assert mpopp(mps) == mps.loop_radius.value + (mps.loop_radius.value * mps.line_length.value)



def test_mp_opp_float(mps):
    mpopp = mps.loop_radius * 2

    assert str(mpopp) == "(loop_radius*2)"

    assert mpopp(mps) == mps.loop_radius.value * 2

