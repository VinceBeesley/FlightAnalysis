from flightanalysis.schedule.elements import Line
from geometry import Transformation, Euler, P0, Point, PX
from flightplotting import plotsec
import numpy as np
from flightanalysis import State


el = Line(30, 100, np.radians(180), "test")

att = Euler(0, np.radians(20), 0)

tp = el.create_template(State.from_transform(
    Transformation(P0(), att),
    vel=att.inverse().transform_point(PX(30))
))

plotsec(tp, nmodels=3, scale=2).show()

