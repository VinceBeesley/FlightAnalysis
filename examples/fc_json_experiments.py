from flightanalysis.fc_json import FCJson
from io import open
from json import dump
from flightplotting.plots import plotsec, plotdtw
from examples.model import obj

with open("examples/UK_England_Bristol_AMARC2002_F3A_P21_21_08_12_00000026.json") as f:
    fcj = FCJson.parse_fc_json(f)



#plotsec(fcj.schedule.manoeuvres[5].get_data(fcj.sec), obj, 5, 10).show()


plotdtw(fcj.sec, fcj.schedule.manoeuvres).show()