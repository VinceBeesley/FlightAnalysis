
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
track_angle = lambda x: abs(x/0.2617993877991494)
roll_angle = lambda x: abs(2.5*x**1.8) # I think this is more like a human judge

from . import Criteria, Continuous, Comparison, free

single_track = Criteria(track_angle, "absolute")
single_roll = Criteria(roll_angle, "absolute")

intra_track = Continuous(track_angle, "absolute")
intra_roll = Continuous(roll_angle, "absolute")
intra_radius = Continuous(radius, "ratio")
intra_speed = Continuous(speed, "ratio")
intra_roll_rate = Continuous(roll_rate, "ratio")

inter_radius = Comparison(radius, "ratio")
inter_speed = Comparison(speed, "ratio")
inter_length = Comparison(length, "ratio")
inter_roll_rate = Comparison(roll_rate, "ratio")
inter_free = Comparison(free, "ratio")