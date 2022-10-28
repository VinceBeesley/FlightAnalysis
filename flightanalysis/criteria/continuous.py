import numpy as np
import pandas as pd
from typing import Callable
from flightanalysis.base.collection import Collection
from . import Result, Criteria
import inspect

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
    """Continous criteria return two error values, one some of difference in positive direction, the other negative
    The downgrades from each of these are truncated before being summed. 
    The remainder goes into a carry over value, which may be added to the downgrade a subsequent continuos criteria.
    """
    def __init__(self, name:str, errors:np.ndarray, downgrades: np.ndarray):
        self.carry_over = downgrades % 0.5
        super().__init__(name, errors, np.trunc(downgrades * 2) / 2)


class Continuous(Criteria):
    def __init__(self,  lookup: Callable, preprocess: Callable=None): 
        super().__init__(lookup, preprocess)

    def __call__(self, name, data: pd.Series, carry_over: np.ndarray= None):
        pdata = self.preprocess(data)
        peak_locs = get_peak_locs(pdata)
        trough_locs = get_peak_locs(pdata, True)

        mistakes = pdata[peak_locs].to_numpy() - pdata[trough_locs].to_numpy()

        errors = np.array([np.sum(mistakes[mistakes > 0]), -np.sum(mistakes[mistakes < 0])])
        downgrades = self.lookup(errors) + (carry_over if carry_over is not None else np.zeros(2, dtype=float))

        return ContinuousResult(
            name,
            errors,  
            downgrades 
        )

    def to_dict(self):
        return dict(
            kind = self.__class__.__name__,
            lookup = inspect.get_source_lines(self.lookup)[0][0],
            preprocess = inspect.get_source_lines(self.preprocess)[0][0]
        )

    @staticmethod
    def from_dict(data:dict):
        return Continuous(eval(data["lookup"]),eval(data["preprocess"]))
