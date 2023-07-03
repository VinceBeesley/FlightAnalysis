from __future__ import annotations
import numpy as np
from . import Criteria
from flightanalysis.schedule.scoring.measurement import Measurement


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

    def __call__(self, m: Measurement):
        data = self.preprocess(m.value, m.expected) * m.visibility
        peak_locs = Continuous.get_peak_locs(data) 
        trough_locs = Continuous.get_peak_locs(data, True)

        mistakes = data[peak_locs] - data[trough_locs]

        errors = np.array([np.sum(mistakes[mistakes > 0]), -np.sum(mistakes[mistakes < 0])])
        downgrades = self.lookup(errors)

        return downgrades
