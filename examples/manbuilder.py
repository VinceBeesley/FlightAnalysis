from flightanalysis.schedule import *
import numpy as np
from flightanalysis.schedule.definition.manoeuvre_builder import f3amb
from flightanalysis.criteria import *


mdef = f3amb.create(ManInfo("Inverted Spin",  "iSp",  4, Position.CENTRE,
            BoxLocation(Height.TOP, Direction.UPWIND, Orientation.INVERTED),
            BoxLocation(Height.BTM)
        ),[
            f3amb.spin(2.5),
            #f3amb.line(),
            #f3amb.loop(np.pi/2)
        ])

it = mdef.info.initial_transform(170, 1)
man = mdef._create()

tp = man.create_template(it)

from flightplotting import plotsec

plotsec(tp, scale=3, nmodels=2).show()
pass
