from flightanalysis.state import Section
import numpy as np
from geometry import Points


def measure_aoa(self: Section, other:Section=None):
    alpha, beta =  np.arctan(self.gbvel.z/self.gbvel.x), np.arctan(self.gbvel.y/self.gbvel.x)
    if other is not None: 
        alpha =  alpha - np.arctan(other.gbvel.z/other.gbvel.x)
        beta = beta - np.arctan(other.gbvel.y/other.gbvel.x)        
    return alpha, beta


def measure_airspeed(self: Section, wind_vectors: Points) -> np.ndarray:
    return self.gbvel - self.gatt.inverse().transform_point(wind_vectors)


def measure_coefficients(self: Section, mass, q, S):
    return self.gbacc * mass / (q * S)

