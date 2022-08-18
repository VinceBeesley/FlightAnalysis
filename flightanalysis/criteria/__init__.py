import numpy as np
import pandas as pd
from typing import List, Dict


dgs = np.linspace(0.5, 10, 20)
f3aangles = np.linspace(2.5, 145, 20)
imacangles = np.linspace(2.5, 97.5, 20)

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


angle_f3a = AngleCrit.build(dgs,f3aangles, 2 * np.pi)
rotation_f3a = AngleCrit.build(dgs,f3aangles)
angle_imac = AngleCrit.build(dgs,imacangles, 2 * np.pi)
rotation_imac = AngleCrit.build(dgs,imacangles)
angle_free = AngleCrit(pd.Series({0.0:0.0}))

