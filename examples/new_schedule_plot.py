from flightanalysis.data.p23 import create_p23
from flightanalysis.schedule.definition.schedule_definition import SchedDef
from geometry import P0, Euler, Transformation, Point
from json import dump
import numpy as np

p23_def:SchedDef = create_p23(1)

p23, template = p23_def.create_template(170, 1)



from flightplotting import plotsec

plotsec(template).show()
