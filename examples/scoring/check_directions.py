from flightanalysis import SchedDef, ManDef
from flightplotting import plotsec
from copy import deepcopy

m: ManDef = SchedDef.load('p23').M

itrans = m.info.initial_transform(170, 1)
corrected = m.create(itrans)

intended = corrected.copy()

intended.elements.e_7_roll.roll = -intended.elements.e_7_roll.roll
fl = intended.create_template(itrans)
#plotsec(fl).show()
intended = intended.copy_directions(corrected)

int_tp = intended.create_template(itrans, fl)
#plotsec(int_tp).show()

el = intended.elements.e_7_roll
fl_e7 = el.get_data(fl)
tp_e7 = el.get_data(int_tp)

res = el.intra_scoring.roll_angle(fl_e7, tp_e7, tp_e7[0].transform)

pass

