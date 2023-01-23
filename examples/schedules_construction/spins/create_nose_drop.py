from flightanalysis.schedule.elements import NoseDrop
from geometry import Transformation, Euler, P0, PX, Point
from flightplotting import plotsec
import numpy as np
from flightanalysis import State

nd = NoseDrop(10, 15, np.radians(45))

att = Euler(np.pi, np.radians(-20), 0)

ndt = nd.create_template(State.from_transform(
    Transformation(P0(), att),
    vel=att.inverse().transform_point(PX(30))
))


nd2 = NoseDrop(15,30,np.radians(25))


nd3 = nd2.match_intention(Transformation(), ndt)

print(nd==nd3)



plotsec(ndt, nmodels=3, scale=2).show()