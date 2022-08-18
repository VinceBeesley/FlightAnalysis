import numpy as np
import pandas as pd
from typing import List, Dict, Callable
from .results import Result, Results

f3a_radius = lambda x : (1 - 1/(x+1)) * 4
f3a_angle = lambda x: x/15
f3a_speed = lambda x : (1 - 1/(x+1))
imac_angle = lambda x: x/10


class Criteria:
    """This class creates a function to return scores for a set of angle errors. 
    """
    def __init__(self, lookup: Callable, preprocess=Callable):
        """build an anglecrit

        Args:
            levels (pd.Series): a pd.series index on error, values are the scores to give
            moduli (float, optional): perform error % moduli on the errors before comparison, None if
                                        you don't want this
        """
        self.lookup = lookup
        self.preprocess = preprocess
    

    def __call__(self, name: str, data: np.ndarray) -> List[float]:
        """get a Result object for a set of errors."""
        pdata = self.preprocess(data)
        return Result(name,data,self.lookup(pdata))

    @property
    def degrees(self):
        return pd.Series(self.levels.values, np.degrees(self.levels.index))

    @staticmethod
    def build(scores, angles, moduli=None):
        return Criteria(pd.concat([pd.Series([0], [0]), pd.Series(scores, np.radians(angles))]), moduli)


basic_angle_f3a = Criteria(f3a_angle, lambda x : np.abs(x % 2* np.pi))

from .continuous import Continuous

intra_f3a_angle = Continuous(lambda x: x/15, lambda x: np.degrees(x))
intra_f3a_radius = Continuous(lambda x : (1 - 1/(x+1)) * 4, lambda x: (x / x[0] - 1) )
intra_f3a_speed = Continuous(lambda x : (1 - 1/(x+1)), lambda x: (x / x[0] - 1) )

from .combination import Combination

