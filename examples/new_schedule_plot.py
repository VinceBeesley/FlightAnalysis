from flightanalysis.data.p23 import create_p23
from flightanalysis.schedule import *
from flightanalysis.schedule.definition import *
from geometry import P0, Euler, Transformation, Point
import json
import numpy as np

p23_def:SchedDef = create_p23(1)

#p23, template = p23_def.create_template(170, 1)
mandef: ManDef = p23_def[0]

itrans = mandef.info.initial_transform(170, 1)
man: Manoeuvre = mandef.create(itrans)
template = man.create_template(itrans)


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)

print(json.dumps(mandef.to_dict(), cls=NumpyEncoder))

from flightplotting import plotsec

plotsec(template, nmodels=20, scale=10).show()
