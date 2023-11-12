from flightanalysis.schedule import *
import numpy as np
from flightanalysis import *

mdef = imacmb.create(ManInfo(
            "Loop", "Lp", k=28, position=Position.CENTRE, 
            start=BoxLocation(Height.BTM, Direction.DOWNWIND, Orientation.UPRIGHT), 
            end=BoxLocation(Height.BTM)
        ),[
            imacmb.loop(np.pi*5/8),
            
        ]
    )




it = mdef.info.initial_transform(170, 1)
man = mdef.create(it)

tp = man.create_template(it)

from flightplotting import plotsec, boxtrace
fig = plotsec(tp, nmodels=20)
fig.add_traces(boxtrace())
fig.show()

