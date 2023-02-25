from flightanalysis.schedule import *
import numpy as np
from flightanalysis.schedule.definition.manoeuvre_builder import f3amb
from flightanalysis.criteria import *


mdef = f3amb.create(ManInfo("Humpty Bump",  "hB2",  3, Position.END,
            BoxLocation(Height.BTM, Direction.UPWIND, Orientation.UPRIGHT),
            BoxLocation(Height.BTM)
        ),[
            f3amb.loop(np.pi/2),
            f3amb.roll("roll_option[0]"),
            f3amb.loop(np.pi),
            f3amb.roll("roll_option[1]"),
            f3amb.loop(-np.pi/2)   
        ], 
        roll_option=ManParm("roll_option", Combination(
            [
                [np.pi, np.pi],
                [np.pi, -np.pi],
                [-np.pi, np.pi],
                [-np.pi, -np.pi],
                [np.pi*1.5, -np.pi/2], 
                [-np.pi*1.5, np.pi/2]
            ]), 0
        )
    )


it = mdef.info.initial_transform(170, 1)
man = mdef.create(it)

tp = man.create_template(it)

from flightplotting import plotsec

plotsec(tp, scale=3, nmodels=20).show()
pass