from json import load
from flightanalysis.state import State
from flightanalysis.flightline import Box
from flightanalysis.data import get_schedule_definition
from flightanalysis.schedule import *
from flightdata import Flight
from geometry import Transformation

with open("examples/data/manual_F3A_P23_22_05_31_00000350.json", "r") as f:
    data = load(f)


flight = Flight.from_fc_json(data)
box = Box.from_fcjson_parmameters(data["parameters"])
state = State.from_flight(flight, box).splitter_labels(data["mans"])

sdef = get_schedule_definition(data["parameters"]["schedule"][1])

mid = 14

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


from flightplotting import plotsec, plotdtw


fig = plotsec(flown, nmodels=10, color="red")
plotsec(int_tp, nmodels=10, color="blue", fig=fig).show()
plotsec(corr_tp, nmodels=10, color="green", fig=fig).show()

plotdtw(aligned, man.all_elements()).show()



