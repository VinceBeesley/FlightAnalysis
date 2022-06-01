from flightanalysis import State, Line, Loop, Snap, Spin
from flightplotting import plotsec
from geometry import Transformation

from flightanalysis import get_schedule

p23 = get_schedule("F3A", "F23")

sched = p23.scale_distance(170).create_raw_template("right", 30, 170, False)
plotsec(sched).show()