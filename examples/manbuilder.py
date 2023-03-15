from flightanalysis.schedule import *
import numpy as np
from flightanalysis.schedule.definition.manoeuvre_builder import f3amb
from flightanalysis.criteria import *


mdef = f3amb.create(ManInfo("Triangular Loop", "trgle", 3,Position.CENTRE,
        BoxLocation(Height.BTM, Direction.DOWNWIND, Orientation.UPRIGHT),
        BoxLocation(Height.BTM)
    ),[
        f3amb.roll("1/2", padded=False),
        f3amb.line(length="((line_length*0.7071067811865476)-((0.5*np.pi)*(speed/partial_roll_rate)))"),
        f3amb.loop(-np.pi*3/4),
        f3amb.roll("2x4"),
        f3amb.loop(np.pi/2),
        f3amb.roll("2x4"),
        f3amb.loop(-np.pi*3/4),
        f3amb.line(length="((line_length*0.7071067811865476)-((0.5*np.pi)*(speed/partial_roll_rate)))"),
        f3amb.roll("1/2", padded=False)
    ])

it = mdef.info.initial_transform(170, 1)
man = mdef.create(it)

tp = man.create_template(it)

from flightplotting import plotsec

plotsec(tp, scale=3, nmodels=20).show()
pass