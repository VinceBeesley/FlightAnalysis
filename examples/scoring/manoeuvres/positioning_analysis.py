from flightanalysis import ManoeuvreAnalysis as MA
from flightanalysis.manoeuvre_analysis import ElementAnalysis as EA
from json import load, dumps
import numpy as np

with open('examples/scoring/manoeuvres/mans/trgle.json', 'r') as f:
    ma = MA.from_dict(load(f))


res = ma.positioning()
pass