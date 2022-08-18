import numpy as np
import pandas as pd
from typing import List, Dict, Callable
from .results import Result, Results

#These functions return scores for an error
f3a_radius = lambda x : (1 - 1/(x+1)) * 4
f3a_length = lambda x : (1 - 1/(x+1)) * 4
f3a_angle = lambda x: x/15
f3a_speed = lambda x : (1 - 1/(x+1))
f3a_roll_rate = lambda x : (1 - 1/(x+1))
imac_angle = lambda x: x/10
hard_zero = lambda x: 0 if x==0 else 10
free = lambda x: 0

class Criteria:
    """This class creates a function to return scores for a set of errors. 
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


basic_angle_f3a = Criteria(f3a_angle, lambda x : np.abs(x % 2* np.pi))


from .continuous import Continuous, ContinuousResult

intra_f3a_angle = Continuous(f3a_angle, lambda x: np.degrees(x))
intra_f3a_radius = Continuous(f3a_radius, lambda x: (x / x[0] - 1) )
intra_f3a_speed = Continuous(f3a_speed, lambda x: (x / x[0] - 1) )

from .comparison import Comparison

inter_f3a_radius = Comparison(f3a_radius, None)
inter_f3a_speed = Comparison(f3a_speed, None)
inter_f3a_length = Comparison(f3a_length, None)
inter_f3a_roll_rate = Comparison(f3a_roll_rate, None)
inter_free = Comparison(free, None)


from .combination import Combination
