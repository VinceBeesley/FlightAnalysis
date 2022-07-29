from pytest import fixture

from flightanalysis.schedule.definition import *
from flightanalysis.schedule.elements import *
from flightanalysis.criteria.comparison import *


#@fixture
def vline():
    md = ManDef(
        "vline",
        ManParms.from_list([
            ManParm("s", f3a_speed, 30, []),
            ManParm("r", f3a_radius, 100, []), 
            ManParm("l", f3a_length, 100, []), 
            ManParm("rate", f3a_roll_rate, 1, []),
        ])
    )

    ps = md.add_loop("e1", "s", "r", -np.pi/2, 0)
    md.mps.parms["s"].append(ps["speed"])  # TODO I think these functions don't work
    md.mps.parms["r"].append(ps["radius"])

    ps = md.add_roll_centred("e2", "s", "l", "rate", np.pi/2)
    md.mps.add(ManParm("e2pad", f3a_length, None, ps["pad_length"]))
    md.mps.parms["s"].append(ps["speed"])
    md.mps.parms["l"].append(ps["length"])


    ps=md.add_loop("e3", "s", "r", np.pi/2, 0)
    md.mps.parms["s"].append(ps["speed"])
    md.mps.parms["r"].append(ps["radius"])

    return md

def test_vline(vline):
    man=vline.create()
    pass

from geometry import Transformation

mdef = vline()
man = mdef.create()
template = man.create_template(Transformation())

downgrades = mdef.mps.collect(man)


from flightplotting import plotsec


plotsec(template, nmodels=5).show()
pass