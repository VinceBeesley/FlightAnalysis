from flightanalysis.schedule.definition.maninfo import *
import numpy as np
from pytest import fixture


def minf(position, direction):
    return ManInfo("test", "t", 1, position, 
        BoxLocation(Height.BTM, direction, Orientation.UPRIGHT), 
        BoxLocation(Height.BTM))


def test_height():
    assert Height.BTM.calculate(170) == np.tan(np.radians(15)) * 170

def test_roll_angle():
    assert Orientation.UPRIGHT.roll_angle() == np.pi


def test_initial_position():
    assert np.sign(minf(Position.CENTRE, Direction.UPWIND).initial_position(170, -1).x[0]) == -1
    assert np.sign(minf(Position.CENTRE, Direction.DOWNWIND).initial_position(170, -1).x[0]) == 1
    assert minf(Position.END, Direction.DOWNWIND).initial_position(170, -1).x[0] == 0
