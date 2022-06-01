from flightanalysis import State, Line, Loop, Snap
from flightplotting import plotsec
from geometry import Transformation

line = Snap(1).scale(300).create_template(Transformation(), 30)

plotsec(line, nmodels=5).show()


