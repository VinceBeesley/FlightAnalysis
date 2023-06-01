from flightanalysis.schedule import *
import numpy as np
from flightanalysis.schedule.definition.manoeuvre_builder import f3amb
from flightanalysis.criteria import *


mdef = f3amb.create(ManInfo(
            "Roll Combo", "rc", k=4, position=Position.CENTRE, 
            start=BoxLocation(Height.BTM, Direction.UPWIND, Orientation.UPRIGHT),
            end=BoxLocation(Height.BTM)
        ),[
            f3amb.roll([np.pi/2, np.pi/2, np.pi/2, -np.pi/2, -np.pi/2, -np.pi/2]),
        ])

it = mdef.info.initial_transform(170, 1)
man = mdef._create()

tp = man.create_template(it)

from flightplotting import plotsec

plotsec(tp, scale=3, nmodels=2).show()
pass
