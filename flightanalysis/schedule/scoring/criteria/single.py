from __future__ import annotations
import numpy as np
import pandas as pd
from typing import List, Dict, Callable
from . import Criteria
from flightanalysis.schedule.scoring import Result, Results, Measurement
import inspect


class Single(Criteria):
    """This class creates a function to return a score for an error. 
    """
    def __init__(self, lookup: Callable, preprocess: Callable=None, slu=None, spp=None):
        """
        Args:
            lookup (Callable): a function that returns a score for a given error
            preprocess (Callable, optional): A function to apply to the input value to return the error.
        """
        self.lookup = lookup        
        self.slu=slu if slu else inspect.getsourcelines(self.lookup)[0][0].split("=")[1].strip()

        if preprocess is None:
            self.preprocess = lambda x: x
        else:
            self.preprocess = preprocess
        self.spp=spp if spp else inspect.getsourcelines(self.preprocess)[0][0].split("=")[1].strip()

    def __call__(self, measurement: Measurement):
        """get a Result object for a set of errors."""
        return self.lookup(self.preprocess(measurement.read()))
        
    def to_dict(self):
        return dict(
            kind = self.__class__.__name__,
            lookup = self.slu,
            preprocess = self.spp
        )

    @staticmethod
    def from_dict(data:dict) -> Single:
        return Single(
            eval(data["lookup"]),
            eval(data["preprocess"]),
            data["lookup"],
            data["preprocess"]
        )
    