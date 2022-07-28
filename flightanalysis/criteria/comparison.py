
import numpy as np
import pandas as pd



class Comparison:
    def __init__(self, levels: pd.Series):
        self.levels = levels

    def lookup(self,value):
        return self.levels[:value].iloc[-1]

    def compare(self, v1, v2):
        return self.lookup(max(v1, v2) / min(v1,v2))

    def __call__(self, *values):
        vs = [values[0]] + list(values)
        return [self.compare(v1, v2) for v1, v2 in zip(vs[:-1], vs[1:])]
    


f3a_radius = Comparison(pd.Series({
    1.0: 0.0,
    1.2: 0.5,
    1.5: 1.0,
    1.8: 1.5,
    2.0: 2.0,
    3.0: 2.5
}))


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