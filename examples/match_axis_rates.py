import numpy as np
import plotly.graph_objects as go
from flightanalysis import Section
from flightplotting.plots import plotsec, plotdtw
from flightplotting.traces import axis_rate_trace, dtwtrace
import flightplotting.templates
from examples.model import obj
from flightanalysis.schedule import p21
from flightanalysis.schedule.element import get_rates
from geometry import Points
from plotly.subplots import make_subplots

sec = Section.from_flight(
    "test/P21_new.csv", "test/gordano_box.json").subset(106, 505)

basic = p21.scale_distance(170).create_raw_template("left", 50.0, 170.0)

rates = get_rates(sec)
rate_matched = p21.match_rates(rates).create_raw_template(
    "left", rates["speed"], rates["distance"])


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



for man in p21.manoeuvres:
    print(man.name)
    fig = make_subplots(
        1, 
        2,
        specs=[[{'type': 'scene'}, {'type': 'scene'}]])
    fig.update_layout(template="flight3d")
    fig.add_traces(
        dtwtrace(man.get_data(aligned_b), man.elements),
        rows=list(np.full(len(man.elements)+2, 1)),
        cols=list(np.full(len(man.elements)+2, 1))
    )
    fig.add_traces(
        dtwtrace(man.get_data(aligned_m), man.elements, False),
        rows=list(np.full(len(man.elements)+2, 1)),
        cols=list(np.full(len(man.elements)+2, 2))
    )
    fig.show()

