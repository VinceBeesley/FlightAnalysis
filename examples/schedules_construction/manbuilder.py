from flightanalysis.schedule import *
import numpy as np
from flightanalysis import *
from flightanalysis.definition.angles import *


mdef = f3amb.create(ManInfo(
            "Double Immelman", "dImm", k=4, position=Position.CENTRE, 
            start=BoxLocation(Height.BTM, Direction.DOWNWIND, Orientation.INVERTED),
            end=BoxLocation(Height.BTM)
        ),[
            f3amb.roll(r1, padded=False),
            f3amb.loop(r05),
            f3amb.roll("roll_option[0]", padded=False),
            centred(f3amb.line(length=30)),
            f3amb.roll("roll_option[1]", padded=False),
            f3amb.loop(-r05),
            f3amb.roll(r05, padded=False),
        ], loop_radius=100, 
        roll_option=ManParm("roll_option", Combination(
            desired=[[-r025, r025], [r025, -r025]]
        ), 0))




it = mdef.info.initial_transform(170, 1)
man = mdef.create(it)

tp = man.create_template(it)

from flightplotting import plotsec, boxtrace
fig = plotsec(tp, nmodels=20)
fig.add_traces(boxtrace())
fig.show()

