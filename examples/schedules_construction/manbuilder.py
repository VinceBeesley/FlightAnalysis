from flightanalysis.schedule import *
import numpy as np
from flightanalysis.schedule.definition.manoeuvre_builder import f3amb
from flightanalysis.schedule.scoring import *


mdef = f3amb.create(ManInfo(
            "Snap", "Sn", k=2, position=Position.CENTRE, 
            start=BoxLocation(Height.BTM, Direction.UPWIND, Orientation.UPRIGHT),
            end=BoxLocation(Height.BTM)
        ),[
            f3amb.snap(1, padded=False)
        ])

it = mdef.info.initial_transform(170, 1)
man = mdef.create(it)

tp = man.create_template(it)

print(tp[9.2: 9.6].data)
