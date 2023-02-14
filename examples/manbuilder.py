from flightanalysis.schedule import *
import numpy as np
from flightanalysis.schedule.definition.manoeuvre_builder import f3amb


th = f3amb.create(
    ManInfo(
        "Top Hat", "tHat", k=4, position=Position.CENTRE, 
        start=BoxLocation(Height.BTM, Direction.UPWIND, Orientation.UPRIGHT),
        end=BoxLocation(Height.BTM)
    ),
    [
        f3amb.loop(np.pi/2),
        f3amb.roll(np.pi),#"2x4"),
        f3amb.loop(np.pi/2),
        f3amb.roll(np.pi),#"1/2",l=100),
        f3amb.loop(-np.pi/2),
        f3amb.roll(np.pi),#"2x4"),
        f3amb.loop(-np.pi/2)
    ]
)


it = th.info.initial_transform(170, 1)
man = th.create(it)

tp = man.create_template(it)

from flightplotting import plotsec

plotsec(tp).show()
pass