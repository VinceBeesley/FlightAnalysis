from flightanalysis.schedule import *
import numpy as np
from flightanalysis.schedule.definition.manoeuvre_builder import f3amb
from flightanalysis.criteria import *


mdef = f3amb.create(ManInfo(
            "Loop", "lP", k=4, position=Position.CENTRE, 
            start=BoxLocation(Height.BTM, Direction.UPWIND, Orientation.UPRIGHT),
            end=BoxLocation(Height.BTM)
        ),[
            f3amb.loop(np.pi/2),
            f3amb.loop(np.pi/2, roll="roll_option[0]"),
            f3amb.loop(-np.pi/2, roll="roll_option[1]"),
            f3amb.loop(np.pi/2),
        ],
        loop_radius=80,
        roll_option=ManParm(
            "roll_option", 
            Combination([[np.pi, -np.pi], [-np.pi, np.pi]]), 0
        ))


it = mdef.info.initial_transform(170, 1)
man = mdef._create()

tp = man.create_template(it)

from flightplotting import plotsec

plotsec(tp, scale=3, nmodels=10).show()
pass
