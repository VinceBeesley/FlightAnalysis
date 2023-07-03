
import numpy as np

"""
All errors start from 0 (no error).

Generally for ratio errors the input should be calculated as: 
error = max(flown, expected) / min(flown, expected) - 1

For absolute errors the input should be:
error = abs(flown - expected)
"""


radius = lambda x: 4 - 4/(x+1)
length = lambda x: 4 - 4/(x+1)
speed = lambda x: 1 - 1/(x+1)
roll_rate = lambda x: 1 - 1/(x+1)
angle = lambda x: abs(x/0.2617993877991494 % (6.283185307179586))

from . import Criteria, Continuous, Comparison, free

single_angle = Criteria(angle, "absolute")

intra_angle = Continuous(angle, "absolute")
intra_radius = Continuous(radius, "ratio")
intra_speed = Continuous(speed, "ratio")
intra_roll_rate = Continuous(roll_rate, "ratio")

inter_radius = Comparison(radius, "ratio")
inter_speed = Comparison(speed, "ratio")
inter_length = Comparison(length, "ratio")
inter_roll_rate = Comparison(roll_rate, "ratio")
inter_free = Comparison(free, "ratio")