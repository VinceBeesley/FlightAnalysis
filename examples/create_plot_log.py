from flightanalysis import Section
from flightplotting.plots import plotsec
from examples.model import obj

sec = Section.from_flight("test/P21_new.csv","test/gordano_box.json")


plotsec(sec, obj, 10, 10).show()

plotsec(sec.subset(110, 200), obj, 10, 10).show()