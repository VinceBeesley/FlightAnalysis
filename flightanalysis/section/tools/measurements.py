from flightanalysis.section import Section
import numpy as np


def measure_aoa(self: Section, other:Section=None):
    alpha, beta =  np.arctan(self.gbvel.z/self.gbvel.x), np.arctan(self.gbvel.y/self.gbvel.x)
    if other is not None: 
        alpha =  alpha - np.arctan(other.gbvel.z/other.gbvel.x)
        beta = beta - np.arctan(other.gbvel.y/other.gbvel.x)        
    return alpha, beta
