from __future__ import annotations
import numpy as np
from typing import List
from numbers import Number
from . import Criteria



class Combination(Criteria):
    """Handles a series of criteria assessments.
    for example a number of rolls in an element. 
    """
    def __init__(self, desired: List[List[Number]], *args, **kwargs):
        self.desired = np.array(desired)
        super().__init__(*args, **kwargs)

    def __getitem__(self, value: int):
        return self.desired[value]

    def get_errors(self, values: np.ndarray):
        """get the error between values and desired for all the options"""
        return self.desired - np.array(values)

    def get_option_error(self, option: int, values: np.ndarray) -> np.ndarray:
        """The difference between the values and a given option"""
        return np.array(values) - self.desired[option]

    def check_option(self, values) -> int:
        """Given a set of values, return the option id which gives the least error"""
        return np.sum(np.abs(self.get_errors(values)), axis=1).argmin()

    def to_dict(self):
        return dict(
            desired = list(self.desired),
            **super().to_dict()
        )

    def __str__(self):
        return f'Combination({self.lookup}, {self.errortype}, {self.desired})'

    @staticmethod
    def rolllist(rolls, reversable=True) -> Combination:
        rolls = [rolls, [-r for r in rolls]] if reversable else [rolls]
        return Combination(rolls)

    @staticmethod
    def rollcombo(rollstring, reversable=True) -> Combination:
        """Convenience constructor to allow Combinations to be built from strings such as 2X4 or 
        1/2"""
        if rollstring[1] == "/":
            rolls = [float(rollstring[0])/float(rollstring[2])]
        elif rollstring[1] in ["X", "x", "*"]:
            rolls = [1/int(rollstring[2]) for _ in range(int(rollstring[0]))]
        rolls = [r*2*np.pi for r in rolls]
        
        return Combination.rolllist(rolls, reversable)