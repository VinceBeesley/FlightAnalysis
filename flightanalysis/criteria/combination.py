import numpy as np
import pandas as pd
from typing import Union, List
from numbers import Number
from . import dgs, f3aangles, imacangles, AngleCrit





class Combination:
    """Handles a series of anglecrit assessments.
    for example a number of rolls in an element. 
    """
    def __init__(self, desired: List[List[Number]], criteria=angle_free):
        self.desired = desired
        self.criteria = criteria
        
    def __getitem__(self, value):
        return self.desired[value]

    def get_errors(self, *values):
        return np.array(self.desired) - np.array(values)

    def get_option_error(self, option, *values):
        return np.array(values) - np.array(self.desired[option])

    def check_option(self, *values):
        return np.sum(np.abs(self.get_errors(*values)), axis=1).argmin()

    def __call__(self, *values):
        return self.criteria(*list(self.get_option_error(self.check_option(*values), *values)))

    @staticmethod
    def rolllist(rolls, reversable=True):
        rolls = [rolls, [-r for r in rolls]] if reversable else [rolls]
        return Combination(rolls)

    @staticmethod
    def rollcombo(rollstring, reversable=True):
        """Convenience constructor to allow Combinations to be built from strings such as 2X4 or 
        1/2"""
        if rollstring[1] == "/":
            rolls = [float(rollstring[0])/float(rollstring[2])]
        elif rollstring[1] in ["X", "x", "*"]:
            rolls = [1/int(rollstring[2]) for _ in range(int(rollstring[0]))]
        rolls = [r*2*np.pi for r in rolls]
        
        return Combination.rolllist(rolls, reversable)