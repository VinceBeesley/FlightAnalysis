import numpy as np
import pandas as pd
from geometry import Point
from flightanalysis.section import Section
from flightanalysis.model.flow import Flows, Flow
from flightanalysis.controls import Control, Controls
from flightanalysis.model.coefficients import Coefficients



class AeroModel:
    """
    wraps a nxm array.
    where n is the number of control + flow variables
    where m is 6 (body frame force coefficients)
    converts control  + flow to coefficients and back
    """ 
    def __init__(self, derivatives: np.ndarray):
        self.derivatives = derivatives


    def forward(self, control: Controls, flow: Flow) -> Coefficients:
        pass

    def backward(self, coefficients: Coefficients, q) -> tuple(Controls, Flows):
        pass




