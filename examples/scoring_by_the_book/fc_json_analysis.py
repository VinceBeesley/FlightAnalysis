from json import load
from flightanalysis.state import State
from flightanalysis.flightline import Box
from flightanalysis.data import get_schedule_definition
from flightanalysis.schedule import *
from flightdata import Flight
from geometry import Transformation, Quaternion
import numpy as np


with open("examples/data/manual_F3A_P23_22_05_31_00000350.json", "r") as f:
    data = load(f)


flight = Flight.from_fc_json(data)
box = Box.from_fcjson_parmameters(data["parameters"])
state = State.from_flight(flight, box).splitter_labels(data["mans"])
sdef = get_schedule_definition(data["parameters"]["schedule"][1])



mid = 1

flown = state.get_meid(mid)
mdef: ManDef = sdef[mid-1]

wind = mdef.info.start.d.get_wind(flown.direction()[0])

itrans = Transformation(
    flown[0].pos,
    mdef.info.start.initial_rotation(wind)
)

man = Manoeuvre.from_all_elements(mdef.info.short_name, mdef.create(itrans).all_elements(True))
tp = man.create_template(itrans)

dist, aligned = State.align(flown, tp, radius=10)

intended, outst = man.match_intention(tp[0], aligned)
int_tp = intended.create_template(itrans, aligned)

dist, aligned = State.align(flown, int_tp, radius=10, mirror=False)

intended, outst = man.match_intention(tp[0], aligned)
int_tp = intended.create_template(itrans, aligned)


mdef.mps.update_defaults(intended)
corr = Manoeuvre(intended.entry_line, mdef._create().elements, mdef.info.short_name)
corr = Manoeuvre.from_all_elements(corr.uid, corr.all_elements(exit_line=True))
corr_tp = corr.create_template(itrans, aligned)



pos_error = aligned.pos - corr_tp.pos
roll_error = Quaternion.body_axis_rates(aligned.att, corr_tp.att).x

#TODO factor by visibility, replace abs here with something cleverer
pos_dg = np.cumsum(abs(pos_error) * aligned.dt / 1000)
roll_dg = np.cumsum(np.abs(roll_error) * aligned.dt / 50)

print(f"score = {10 - pos_dg[-1] - roll_dg[-1]}")


from flightplotting import plotsec, plotdtw


fig = plotsec(flown, nmodels=10, color="red")
fig = plotsec(int_tp, nmodels=10, color="blue", fig=fig)
plotsec(corr_tp, nmodels=10, color="green", fig=fig).show()

#plotdtw(aligned, man.all_elements()).show()


import plotly.graph_objects as go

fig = go.Figure()

fig.add_trace(go.Line(y=pos_dg))
fig.add_trace(go.Line(y=roll_dg , yaxis="y2"))
fig.update_layout(
    yaxis=dict(
        title="position error"
    ), 
    yaxis2=dict(title="roll error",
        overlaying="y",
        side="right",)
)
fig.show()
