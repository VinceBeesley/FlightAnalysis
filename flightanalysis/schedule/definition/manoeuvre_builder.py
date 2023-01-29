"""Playing with ways to simpliy all the helper functions in the ManDef class"""

from . import ManDef, ManParm, ManParms, ElDef, ElDefs
from flightanalysis.schedule.elements import *
from typing import Dict, List
from numbers import Number


class ManoeuvreBuilder():
    default_mps = ManParms()

    def __init__(self, mps: ManParms, mpmaps:Dict[El, Dict[str: str]]):
        self.mps = mps
        self.mpmaps = mpmaps

    def base_parms(self, *kwargs):
        mps = self.defaultmps.deep_copy()
        for k,v in kwargs.items():
            if isinstance(v, Number):
                mps.data[k].default = v
            elif isinstance(v, ManParm):
                mps.data[k] = v
        return mps

    def el(self, Kind, *args, **kwargs):
        pass

    def create(self, maninfo, els):
        md = ManDef(maninfo, self.default_mps.deepcopy(), els)
        




F3AMB = ManoeuvreBuilder(
    ManParms([
        ManParm("speed", inter_f3a_speed, 30.0),
        ManParm("loop_radius", inter_f3a_radius, 55.0),
        ManParm("line_length", inter_f3a_length, 130.0),
        ManParm("point_length", inter_f3a_length, 10.0),
        ManParm("continuous_roll_rate", inter_f3a_roll_rate, np.pi/2),
        ManParm("partial_roll_rate", inter_f3a_roll_rate, np.pi/2),
        ManParm("snap_rate", inter_f3a_roll_rate, 4*np.pi),
        ManParm("stallturn_rate", inter_f3a_roll_rate, 2*np.pi),
        ManParm("spin_rate", inter_f3a_roll_rate, 1.7*np.pi),
    ]),
    mpmaps = {
        Line: {
            "roll": 0.0,
            "speed": "speed",
            "length": "line_length"
        },
        Loop: {
            "angle": None,
            "roll": 0.0,
            "ke": False,
            "speed": "speed",
            "radius": "loop_radius"
        },
        StallTurn: {
            "speed": 0.0,
            "yaw_rate": "stallturn_rate"   
        },

    }
)