from flightanalysis.schedule import p21, f21
from flightplotting.plots import plotsec
from examples.model import obj



#temp = p21.scale_distance(170).create_raw_template("left", 30.0, 170)
#plotsec(temp, obj, 10, 10).show()
#
#plotsec(p21.manoeuvres[5].get_data(temp), obj, 10, 10).show()

temp = f21.scale_distance(170).create_raw_template("left", 30.0, 170)
plotsec(temp, obj, 10, 10).show()

plotsec(f21.manoeuvres[5].get_data(temp), obj, 10, 10).show()

