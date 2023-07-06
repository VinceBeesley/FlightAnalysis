from __future__ import annotations
import numpy as np
import pandas as pd
from . import Criteria
from flightanalysis.schedule.scoring import Measurement


class Comparison(Criteria):
    """Works on a discrete set of ratio errors.
    input should be ratio error to the expected (first) value
    output is each compared to the previous value
    """            
    def __call__(self, data: np.ndarray):
        #TODO change to take a measurement and account for visibility
        cval = data[0]

        data = np.concatenate([np.array([cval]), data])
        ratios = self.preprocess(data[:-1], data[1:])
        return self.lookup(np.abs(ratios))


    