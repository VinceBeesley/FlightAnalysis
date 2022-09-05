import numpy as np
import pandas as pd
from typing import Callable
from flightanalysis.base.collection import Collection
from . import Result, Criteria



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


class ContinuousResult(Result):
    def __init__(self, name:str, peaks: pd.Series, troughs: pd.Series, errors: np.ndarray, downgrades: np.ndarray):
        self.peaks = peaks
        self.troughs = troughs
        super().__init__(name, errors, downgrades)


class Continuous(Criteria):
    def __init__(self,  lookup: Callable, preprocess: Callable=None): 
        super().__init__(lookup, preprocess)

    def __call__(self, name, data: pd.Series):
        pdata = self.preprocess(data)
        peak_locs = get_peak_locs(pdata)
        trough_locs = get_peak_locs(pdata, True)
        errors = abs(pdata[peak_locs].to_numpy()) - abs(pdata[trough_locs].to_numpy())
        return ContinuousResult(
            name,
            data[peak_locs],
            data[trough_locs],
            errors,
            self.lookup(errors)
        )


