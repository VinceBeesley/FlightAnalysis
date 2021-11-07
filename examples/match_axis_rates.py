import numpy as np
import plotly.graph_objects as go
from flightanalysis import Section, get_schedule
from flightplotting.plots import plotsec, plotdtw
from flightplotting.traces import axis_rate_trace, dtwtrace
import flightplotting.templates
from flightanalysis.schedule.elements import get_rates
from geometry import Points
from plotly.subplots import make_subplots


def plot_dtw(fig, col:int, elms: list, sec: Section, temp:Section):
    fig.add_traces(
        dtwtrace(man.get_data(sec), elms, showlegend=False),
        rows=list(np.full(len(elms)+2, 1)),
        cols=list(np.full(len(elms)+2, col))
    )
    for tr in axis_rate_trace(man.get_data(sec), True):
        fig.add_trace(tr, row=2, col=col)
    for tr in axis_rate_trace(man.get_data(temp), True):
        fig.add_trace(tr, row=3, col=col)



def plot_man(man, aligned_b, aligned_m):
    print(man.name)
    fig = make_subplots(
        3, 
        2,
        specs=[
            [{'type': 'scene'}, {'type': 'scene'}],
            [{'type': 'xy'}, {'type': 'xy'}],
            [{'type': 'xy'}, {'type': 'xy'}]
            ])
    fig.update_layout(template="flight3d", showlegend=False)
    
    plot_dtw(fig, 1, man.elements, aligned_b, basic)
    plot_dtw(fig, 2, man.elements, aligned_m, rate_matched)

    fig.show()



if __name__ == '__main__':

    sec = Section.from_csv("tests/test_inputs/test_log_00000052_section.csv").subset(110, 200)

    p21 = get_schedule("F3A", "P21")

    basic = p21.scale_distance(170).create_raw_template("left", 30.0, 170.0)

    rates = get_rates(sec)
    rate_matched = p21.match_rates(rates).create_raw_template(
        "left", rates["speed"], rates["distance"])

    fit_qual_b, aligned_b = Section.align(sec, basic, 1)
    fit_qual_m, aligned_m = Section.align(sec, rate_matched, 1)


    print("fit distance basic: {}, matched: {}".format(fit_qual_b, fit_qual_m))



    for man in p21.manoeuvres:
        plot_man(man, aligned_b, aligned_m)