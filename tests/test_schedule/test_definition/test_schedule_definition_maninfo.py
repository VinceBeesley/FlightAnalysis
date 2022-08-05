from flightanalysis.schedule.definition.maninfo import *
import numpy as np


def test_height():
    assert Height.BTM.calculate(170) == np.tan(np.radians(15)) * 170



def test_roll_angle():
    assert Orientation.UPRIGHT.roll_angle() == np.pi

