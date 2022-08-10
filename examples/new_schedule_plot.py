from flightanalysis.data.p23 import create_p23
from flightanalysis.schedule.definition.schedule_definition import SchedDef
from geometry import P0, Euler, Transformation, Point
from json import dump
import numpy as np

p23_def:SchedDef = create_p23(1)
itrans = Transformation(
    Point(0, 170, 50), 
    Euler(np.pi,0,np.pi)
)
man = p23_def.fTrn.create(itrans)
template=man.create_template(itrans)
from flightplotting import plotsec

plotsec(template).show()
