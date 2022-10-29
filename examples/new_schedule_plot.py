from flightanalysis.data.p23 import create_p23
from flightanalysis.schedule.definition.schedule_definition import SchedDef
from geometry import P0, Euler, Transformation, Point
from json import dump
import numpy as np

p23d:SchedDef = create_p23(1)


p23dict = p23d.to_dict()
p23_def = SchedDef.from_dict(p23dict)

itrans = p23_def.tHat.info.initial_transform(170, 1)
man = p23_def.tHat.create(itrans)
template=man.create_template(itrans)
from flightplotting import plotsec

plotsec(template).show()
