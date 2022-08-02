from pytest import fixture


from flightanalysis.schedule.elements import *


def test_rollcombo():
    rc = rollcombo(
        [
            Roll(0.25, 1, 1), 
            Roll(0.25, 1, 1)
        ], 
        30, 500, 5,
        RollPosition.CENTRE
    )

    assert len(rc) == 5
    assert rc[0].rolls==0
    assert rc[1].rolls==0.25


def test_roll():
    rc = roll("3X4", 30, 500, 5, 1, RollPosition.CENTRE)
    assert len(rc) == 7

