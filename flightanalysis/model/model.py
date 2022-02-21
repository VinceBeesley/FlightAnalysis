import numpy as np
import pandas as pd
from geometry import Point
from flightanalysis.section import Section


class ACConstants:
    def __init__(self, s: float, c:float, b:float, mass:float, cg:Point):
        self.s = s
        self.c = c
        self.b = b
        self.mass = mass
        self.cg = cg

cold_draft = ACConstants(0.569124, 0.31211, 1.8594, 4.5, Point(0.6192,0.0,0.0))


class Control(Section):
    """
    handles a time history of control inputs
    """
    def __init__(self, data: pd.DataFrame):
        self.data = data




class Flow:
    """
        handles a time history of flow data
        alpha, beta, q
    """
    def __init__(self, data: pd.DataFrame):
        self.data = data



class Coeffients:

    def __init__(self, data: pd.DataFrame):
        self.data = data


class AeroModel:
    """
    wraps a nxm array.
    where n is the number of control + flow variables
    where m is 6 (body frame force coefficients)

    """ 
    def __init__(self, derivatives: np.ndarray):
        self.derivatives = derivatives

    def calculate_coefficients(self, flow: Flow, control: Control):
        pass

    def calculate_trim(self, coefficients: Coeffients):
        pass







