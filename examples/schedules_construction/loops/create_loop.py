from flightanalysis.schedule.elements import Loop
from geometry import Transformation, Euler, P0, Point, PX
from flightplotting import plotsec
import numpy as np
from flightanalysis import State


el = Loop(30, 100, np.radians(180), np.pi, False)


tp = el.create_template(State.from_transform(Transformation(),vel=PX(30))) 


att = Euler(0, np.radians(20), 0)

fl = el.create_template(State.from_transform(
    Transformation(P0(), att),
    vel=att.inverse().transform_point(PX(30))
))

el_diff = Loop(20, 50, np.radians(180), -np.pi, False)


el2 = el_diff.match_intention(tp[0].transform, fl)

assert el == el2


plotsec(tp, nmodels=3, scale=2).show()

