from flightanalysis import Snap
from flightplotting import plotsec 
from geometry import Transformation
from flightanalysis.base.table import Time
import numpy as np

snap = Snap(30, 1, 2, 1)

dt = np.linspace(1,2, 200)



tp = snap.create_template(Transformation.zero(), Time.from_t(dt.cumsum()).reset_zero())

plotsec(tp, nmodels=10, scale=5).show()
