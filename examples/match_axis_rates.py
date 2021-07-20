from flightanalysis import Section
from flightplotting.plots import plotsec
from flightplotting.traces import axis_rate_trace
from examples.model import obj
from flightanalysis.schedule import p21
from flightanalysis.schedule.element import get_rates
from geometry import Points

sec = Section.from_flight("test/P21_new.csv", "test/gordano_box.json").subset(110, 505)

plotsec(sec, obj, 5, 5, color="blue").show()
basic = p21.scale_distance(170).create_template("left", 30.0, 170.0)

rates = get_rates(sec)
rate_matched = p21.match_rates(rates).create_template(
    "left", rates["speed"], rates["distance"])

#plotsec(sec, obj, 5, 2).show()
#plotsec(rate_matched, obj, 5, 2).show()

from plotly.subplots import make_subplots


fig = make_subplots(rows=3, cols=1)
for tr in axis_rate_trace(sec, True):
    fig.add_trace(tr, row=1, col=1)
for tr in axis_rate_trace(basic, True):
    fig.add_trace(tr, row=2, col=1)
for tr in axis_rate_trace(rate_matched, True):
    fig.add_trace(tr, row=3, col=1)
fig.show()



fit_qual_b, aligned_b = Section.align(sec, basic)
fit_qual_m, aligned_m = Section.align(sec, rate_matched)


print("fit distance basic: {}, matched: {}".format(fit_qual_b, fit_qual_m))

import plotly.graph_objects as go


for man in p21.manoeuvres:
    print(man.name)
    plotsec(man.get_data(aligned_b), obj, 5, 5, color="blue").show()
    plotsec(man.get_data(aligned_m), obj, 5, 5, color="orange").show()
    