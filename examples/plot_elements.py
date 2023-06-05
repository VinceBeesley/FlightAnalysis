from flightanalysis import Snap, Spin
from flightplotting import plotsec 
from geometry import Transformation
from flightanalysis.base.table import Time
import numpy as np

snap = Snap(30, 1, 2, 1)
spin = Spin(10, 2, 2)

tp = spin.create_template(Transformation.zero())

plotsec(tp, nmodels=10, scale=3).show()
