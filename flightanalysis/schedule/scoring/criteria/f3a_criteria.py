
from . import Single, Continuous, Comparison, Combination
import numpy as np
import pandas as pd

def radius(x):
    """calculate the downgrade for a change in radius

    Args:
        x (float): radius ratio - 1

    Returns:
        float: the downgrade
    """
    return (1 - 1/(x+1)) * 4


hard_zero = lambda x: 0 if x==0 else 10

free = lambda x: 0 if not pd.api.types.is_list_like(x) else np.zeros(len(x))
length = lambda x : (1 - 1/(x+1)) * 4
angle = lambda x: x/15
speed = lambda x : (1 - 1/(x+1))
roll_rate = lambda x : (1 - 1/(x+1))


single_angle = Single(angle, lambda x : np.abs(np.degrees(x) % (2 * np.pi)))

intra_angle = Continuous(angle, lambda x: np.degrees(x))
intra_radius = Continuous(radius, lambda x: (x / x[0] - 1) )
intra_speed = Continuous(speed, lambda x: (x / x[0] - 1) )
intra_roll_rate = Continuous(roll_rate, lambda x: np.degrees(x))

inter_radius = Comparison(radius, None)
inter_speed = Comparison(speed, None)
inter_length = Comparison(length, None)
inter_roll_rate = Comparison(roll_rate, None)
inter_free = Comparison(free, None)