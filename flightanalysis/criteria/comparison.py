
import numpy as np
import pandas as pd



class Comparison:
    def __init__(self, levels: pd.Series, initial_value=None):
        self.levels = levels
        self.initial_value = initial_value

    def lookup(self,value):
        return self.levels[:value].iloc[-1]

    def compare(self, v1, v2):
        if v1 is None:
            return 0
        if v1==0 or v2 == 0:
            return 0
        return self.lookup(max(v1, v2) / min(v1,v2))

    def __call__(self, *values):
        if len(values) == 0:
            return []
        vs = [self.initial_value] + list(values)
        return [self.compare(v1, v2) for v1, v2 in zip(vs[:-1], vs[1:])]


class HardZero:
    def __init__(self, dg, initial_value=None):
        self.dg = dg
        self.initial_value = initial_value

    def compare(self, v1, v2):
        if v1 is None:
            return 0
        return 0 if v1==v2 else self.dg

    def __call__(self, *values):
        vs = [self.initial_value] + list(values)
        return [self.compare(v1,v2) for v1, v2 in zip(vs[:-1], vs[1:])]




f3a_direction = lambda direction : HardZero(10, direction)


f3a_radius = Comparison(pd.Series({
    1.0: 0.0,
    1.2: 0.5,
    1.5: 1.0,
    1.8: 1.5,
    2.0: 2.0,
    3.0: 2.5
}))

# TODO this could give very low marks for short lines
f3a_length = Comparison(pd.Series({
    1.0: 0.0,
    1.2: 0.5,
    1.5: 1.0,
    1.8: 1.5,
    2.0: 2.0,
    3.0: 2.5,
    4.0: 3.0
}))

f3a_speed = Comparison(pd.Series({
    1.0: 0.0,
    2.0: 0.5,
    3.0: 1.0,
}))

f3a_roll_rate = Comparison(pd.Series({
    1.0: 0.0,
    1.5: 0.5,
    2.0: 1.0
}))

f3a_free = Comparison(pd.Series({
    1.0: 0.0
}))