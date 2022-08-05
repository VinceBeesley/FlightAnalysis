import numpy as np
import pandas as pd
from typing import Union, List
from numbers import Number


class AngleCrit:
    """This class creates a function to return scores for a set of angle errors. 
    """
    def __init__(self, levels: pd.Series, moduli=None):
        """build an anglecrit

        Args:
            levels (pd.Series): a pd.series index on error, values are the scores to give
            moduli (float, optional): perform error % moduli on the errors before comparison, None if
                                        you don't want this
        """
        self.levels = levels
        self.moduli = moduli
    
    def get_score(self, error):
        if self.moduli:
            error = error % self.moduli
        return self.levels[:abs(error)].iloc[-1]

    def __call__(self, *errors) -> List[float]:
        """get a list of scores for the errors.

        Returns:
            List[float]: the scores
        """
        return [self.get_score(error) for error in errors]

    @property
    def degrees(self):
        return pd.Series(self.levels.values, np.degrees(self.levels.index))

    @staticmethod
    def build(scores, angles, moduli=None):
        return AngleCrit(pd.concat([pd.Series([0], [0]), pd.Series(scores, np.radians(angles))]), moduli)


_dgs = np.linspace(0.5, 10, 20)
angle_f3a = AngleCrit.build(_dgs,np.linspace(2.5, 145, 20), 2 * np.pi)
rotation_f3a = AngleCrit.build(_dgs,np.linspace(2.5, 145, 20))
angle_imac = AngleCrit.build(_dgs,np.linspace(2.5, 97.5, 20), 2 * np.pi)
rotation_imac = AngleCrit.build(_dgs,np.linspace(2.5, 97.5, 20))
angle_free = AngleCrit(pd.Series({0.0:0.0}))


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
    
