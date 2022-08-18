import numpy as np
import pandas as pd
from typing import Callable
from flightanalysis.base.collection import Collection

f3a_angle = lambda error: error/15


def get_peak_locs(arr, rev=False):
    increasing = np.sign(np.diff(np.abs(arr)))>0
    last_downgrade = np.column_stack([increasing[:-1], increasing[1:]])
    peaks = np.sum(last_downgrade.astype(int) * [10,1], axis=1) == (1 if rev else 10)
    last_val = False if rev else increasing[-1]
    first_val = increasing[0] if rev else False
    return np.concatenate([np.array([first_val]), peaks, np.array([last_val])])

def downgradeable_values(arr):
    """subtract the peaks from the troughs and return the difference"""
    if isinstance(arr, pd.Series):
        arr = arr.to_numpy()
    peaks = arr[get_peak_locs(arr)]
    troughs = arr[get_peak_locs(arr, True)]
    return np.abs(peaks) - np.abs(troughs)


class ContinuousResult:
    def __init__(self, peaks: pd.Series, troughs: pd.Series, errors: np.ndarray, downgrades: np.ndarray):
        self.peaks = peaks
        self.troughs = troughs
        self.errors = errors
        self.downgrades = downgrades
        self.value = sum(self.downgrades)
        self.downgrade = np.trunc(self.value * 2) / 2


class ContinuousResults(Collection):
    def downgrade(self):
        return sum([cr.downgrade for cr in self])



class Continuous:
    def __init__(self,  lookup: Callable, preprocess: Callable): 
        self.lookup = lookup
        self.preprocess = preprocess

    def __call__(self, data: pd.Series):
        pdata = self.preprocess(data)
        peak_locs = get_peak_locs(pdata)
        trough_locs = get_peak_locs(pdata, True)
        errors = abs(pdata[peak_locs].to_numpy()) - abs(pdata[trough_locs].to_numpy())
        return ContinuousResult(
            data[peak_locs],
            data[trough_locs],
            errors,
            self.lookup(errors)
        )


intra_f3a_angle = Continuous(lambda x: x/15, lambda x: np.degrees(x))
intra_f3a_radius = Continuous(lambda x : (1 - 1/(x+1)) * 4, lambda x: (x / x[0] - 1) )
intra_f3a_speed = Continuous(lambda x : (1 - 1/(x+1)), lambda x: (x / x[0] - 1) )