
from flightanalysis.section.variables import SVar

from collections import namedtuple


FDConstants = namedtuple(
    "FDConstants", 
    [
        "S", # Wing Area, m**2 
        "MTOW", # mass, kg
        "MAC", # Mean Aerodynamic Chord, m
        "w", # wing span, m
        "Inertia", # Inertia Matrix kg * m**2
   ])

FDInputs = namedtuple(
    "FDInputs", [
        "aspd", 
        "alpha", 
        "beta", 
        "brvel"
])

FDOutputs = namedtuple(
    "FDOutputs", [
        "bacc", 
        "bracc"
])
