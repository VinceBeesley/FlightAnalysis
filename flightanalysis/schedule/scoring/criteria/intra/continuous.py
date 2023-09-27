from __future__ import annotations
import numpy as np
import numpy.typing as npt
import pandas as pd
from .. import Criteria
from dataclasses import dataclass
from geometry import Point

@dataclass
class Continuous(Criteria):
    """Works on a continously changing set of values. 
    only downgrades for increases (away from zero) of the value.
    treats each separate increase (peak - trough) as a new error.
    """
    @staticmethod
    def get_peak_locs(arr, rev=False):
        increasing = np.sign(np.diff(np.abs(arr)))>0
        last_downgrade = np.column_stack([increasing[:-1], increasing[1:]])
        peaks = np.sum(last_downgrade.astype(int) * [10,1], axis=1) == (1 if rev else 10)
        last_val = False if rev else increasing[-1]
        first_val = increasing[0] if rev else False
        return np.concatenate([np.array([first_val]), peaks, np.array([last_val])])

    @staticmethod
    def smooth_sample(values, window_width=10):
        window_width = min(window_width, int(len(values)/2))
        cumsum_vec = np.cumsum(np.insert(values, 0, 0)) 
        ma_vec = (cumsum_vec[window_width:] - cumsum_vec[:-window_width]) / window_width
        return ma_vec

    def prepare(self, value: npt.NDArray, expected: float):
        if self.comparison == 'absolute':
            return abs(expected - value)
        elif self.comparison == 'ratio':
            return abs(value)
        else:
            raise ValueError('self.comparison must be "absolute" or "ratio"')

    def __call__(self, ids: npt.ArrayLike, values: npt.ArrayLike):
        data = np.array(values)
        peak_locs = Continuous.get_peak_locs(data)
        trough_locs = Continuous.get_peak_locs(data, True)

        if self.comparison == 'absolute':
            #if absolute, we only care about increases in error, corrections are free
            mistakes = np.abs(data[peak_locs] - data[trough_locs])
            dgids = list(np.array(ids)[peak_locs])
        elif self.comparison == 'ratio':
            #if ratio then all changes are downgraded
            values = np.concatenate([[data[0]], data[peak_locs + trough_locs]])
            mistakes = np.maximum(values[:-1], values[1:]) / np.minimum(values[:-1], values[1:]) - 1
            dgids = list(np.array(ids)[peak_locs + trough_locs])# + [ids[-1]]
        else:
            raise ValueError(f'{self.comparison} not in [absolute, ratio]')
        
        downgrades = self.lookup(mistakes)

        return dgids, mistakes, downgrades
