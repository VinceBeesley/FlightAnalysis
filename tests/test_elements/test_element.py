import numpy as np
import unittest
from flightanalysis.schedule.elements import El
import pytest


class SubEl(El):
    def __init__(self, arg1, arg2, uid: str = None):
        super().__init__(uid)
        self.arg1 = arg1
        self.arg2 = arg2



def test_uid():
    se = SubEl(2, 3)
    assert se.uid == 1
    