from flightanalysis.schedule import p21
from flightplotting.plots import plotsec
from examples.model import obj




plotsec(p21.create_template("left", 170), obj, 10, 10).show()
