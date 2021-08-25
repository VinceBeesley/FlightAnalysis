from flightanalysis.fc_json import FCJson
from io import open
from json import dump
from flightplotting.plots import plotsec, plotdtw
from flightplotting.traces import dtwtrace
import flightplotting.templates
from examples.model import obj

with open("examples/UK_England_Bristol_AMARC2002_F3A_P21_21_08_12_00000026.json") as f:
    fcj = FCJson.parse_fc_json(f)



#plotsec(fcj.schedule.manoeuvres[5].get_data(fcj.sec), obj, 5, 10).show()


plotdtw(fcj.sec, fcj.schedule.manoeuvres).show()



import plotly.graph_objects as go

for man in fcj.schedule.manoeuvres[1:]:
    fig = go.Figure()
    fig.update_layout(template="flight3d", showlegend=False)

    fig.add_traces(
            dtwtrace(man.get_data(fcj.sec), man.elements, showlegend=False)
        )
    fig.show()
    pass
