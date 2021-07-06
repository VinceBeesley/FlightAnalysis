from flightanalysis.schedule import p21
from flightplotting.plots import plotsec
from examples.model import obj



temp = p21.create_template("left", 170)
plotsec(temp, obj, 10, 10).show()

plotsec(p21.manoeuvres[5].get_data(temp), obj, 10, 10).show()

