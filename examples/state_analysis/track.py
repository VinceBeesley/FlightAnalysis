from flightanalysis.schedule.elements import Loop, Line
from flightanalysis.schedule.scoring.measurement import Measurement
import numpy as np
from flightanalysis import State
from geometry import Transformation, PX, Point, Euldeg

from flightplotting import plotsec


line = Line(30, 100, np.radians(90))
ist = State.from_transform(Transformation.zero())

tp = line.create_template(ist)

fl = Loop(30, 1000, np.radians(10),  np.radians(90)).create_template(ist)

line = line.match_intention(ist.transform, fl)

tp = line.create_template(ist, fl.time)

fig = plotsec(fl)

plotsec(tp, fig=fig).show()

meas = Measurement.track_z(fl, tp, tp[0].transform)


pass