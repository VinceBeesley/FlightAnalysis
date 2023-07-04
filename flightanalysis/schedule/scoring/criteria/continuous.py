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

    def smooth_sample(self, values, window_width=10):
        cumsum_vec = np.cumsum(np.insert(values, 0, 0)) 
        ma_vec = (cumsum_vec[window_width:] - cumsum_vec[:-window_width]) / window_width
        return ma_vec


    def __call__(self, m: Measurement):
        data = self.preprocess(m.value, m.expected) * m.visibility
        data = self.smooth_sample(data, 10)
        peak_locs = Continuous.get_peak_locs(data) 
        trough_locs = Continuous.get_peak_locs(data, True)

        mistakes = data[peak_locs] - data[trough_locs]

        errors = np.array([np.sum(mistakes[mistakes > 0]), -np.sum(mistakes[mistakes < 0])])
        downgrades = self.lookup(errors)

        return downgrades
