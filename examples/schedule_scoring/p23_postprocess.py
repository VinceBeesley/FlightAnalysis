from flightdata import Flight
import numpy as np
from flightanalysis import State, Box
from flightanalysis.data.p23 import p23_def
from flightplotting import plotsec, plotdtw
from os.path import exists
from geometry import Transformation, Point, Euler
from pathlib import Path

flown = State.from_flight(
    Flight.from_csv("examples/data/p23_example.csv"), 
    Box.from_f3a_zone("examples/data/p23_box.f3a")
)[103:462]

wind=np.sign(flown[0].vel.x[0])
p23, template = p23_def.create_template(flown.pos.y.mean(), wind)

aligned_path = Path("examples/schedule_scoring/aligned.csv")
dist, aligned = State.align(flown, template, 10)


intended = p23.match_intention(template[0].transform, aligned)


#
#
#intended_template = intended.create_template(Transformation(
#    aligned[0].pos,
#    aligned[0].att.closest_principal()
#))
#
#dist, aligned2 = State.align(flown, intended_template, 20, False)
#
#intended2 = p23.match_intention(template[0].transform, aligned2)
#
#intended_template = intended2.create_template(Transformation(
#    aligned2[0].pos,
#    aligned2[0].att.closest_principal()
#))
#
#
#plotdtw(intended_template, p23).show()