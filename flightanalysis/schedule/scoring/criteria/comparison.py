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
    def __str__(self):
        return f'Comparison({self.lookup}, {self.errortype})'   

    def __call__(self, data: np.ndarray):
        cval = data[0]

        data = np.concatenate([np.array([cval]), data])
        ratios = self.preprocess(data[:-1], data[1:])
        return self.lookup(np.abs(ratios))


    