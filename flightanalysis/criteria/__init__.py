from argparse import ArgumentTypeError
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

from .single import Single

basic_angle_f3a = Single(f3a_angle, lambda x : np.abs(np.degrees(x) % (2 * np.pi)))

from .continuous import Continuous, ContinuousResult

intra_f3a_angle = Continuous(f3a_angle, lambda x: np.degrees(x))
intra_f3a_radius = Continuous(f3a_radius, lambda x: (x / x[0] - 1) )
intra_f3a_speed = Continuous(f3a_speed, lambda x: (x / x[0] - 1) )
intra_f3a_roll_rate = Continuous(f3a_roll_rate, lambda x: np.degrees(x))

from .comparison import Comparison

inter_f3a_radius = Comparison(f3a_radius, None)
inter_f3a_speed = Comparison(f3a_speed, None)
inter_f3a_length = Comparison(f3a_length, None)
inter_f3a_roll_rate = Comparison(f3a_roll_rate, None)
inter_free = Comparison(free, None)

from .combination import Combination

criteria = [Single, Continuous, Combination, Comparison]

def criteria_from_dict(data):
    for crit in criteria:
        if crit.__name__ == data["kind"]:
            return crit.from_dict(data)
    raise ValueError("unknown criteria")
        