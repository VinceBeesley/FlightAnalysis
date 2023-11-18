from flightanalysis.schedule import *
import numpy as np
from flightanalysis.schedule.definition.manoeuvre_builder import *
from flightanalysis.schedule.scoring import *


mdef = f3amb.create(ManInfo(
        "Spin", "iSpin", k=3, position=Position.CENTRE, 
        start=BoxLocation(Height.TOP, Direction.UPWIND, Orientation.INVERTED),
        end=BoxLocation(Height.BTM),
    ),[
        MBTags.CENTRE,
        f3amb.spin(2),
        f3amb.roll("1/2", line_length=165),
        f3amb.loop(np.pi/2),
    ])

it = mdef.info.initial_transform(170, 1)
man = mdef.create(it)

tp = man.create_template(it)

from flightplotting import plotsec, boxtrace
fig = plotsec(tp)
fig.add_traces(boxtrace())
fig.show()

