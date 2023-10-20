from flightanalysis.schedule import *
import numpy as np
from flightanalysis.schedule.definition.manoeuvre_builder import *
from flightanalysis.schedule.scoring import *
from examples.schedules_construction.f25 import f25_def



for i in range(0, 17, 2):
    mdef = f25_def[i]

    it = mdef.info.initial_transform(170, 1)
    man = mdef.create(it)

    tp = man.create_template(it)

    from flightplotting import plotsec, boxtrace
    fig = plotsec(tp)
    fig.add_traces(boxtrace())
    fig.show()

