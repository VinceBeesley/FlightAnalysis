from flightanalysis import Section
from flightplotting.plots import plotsec
from examples.model import obj
from flightanalysis.schedule import p21
from geometry import Points

sec = Section.from_flight("test/P21_new.csv","test/gordano_box.json")

rate_matched = p21.match_rates(sec)

plotsec(sec, obj, 5, 2).show()
plotsec(rate_matched, obj, 5, 2).show()
