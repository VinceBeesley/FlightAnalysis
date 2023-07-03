from . import ManDef, ManParm, ManParms, ElDef, ElDefs
from flightanalysis.schedule.elements import *

from typing import Dict, List
from numbers import Number
from functools import partial
from .element_builders import *
from numbers import Number


class MBTags:
    CENTRE=0


class ManoeuvreBuilder():
    def __init__(self, mps: ManParms, mpmaps:Dict[str, dict]):
        self.mps = mps
        self.mpmaps = mpmaps

    def __getattr__(self, name):
        if name in self.mpmaps:
            return partial(self.el, name)
    
    def el(self, kind, *args, **kwargs):
        #setup kwargs to pull defaults from mpmaps
        #returns a function that appends the created elements to a ManDef
        
        all_kwargs = self.mpmaps[kind]["kwargs"].copy() # take the defaults
        for k,a in kwargs.items():
            assert not k in self.mpmaps[kind]["args"]
            all_kwargs[k]=a  # take the **kwargs if they were specified
        for k, a in zip(self.mpmaps[kind]["args"], args):
            all_kwargs[k] = a  # take the *args
        
        def append_el(md: ManDef, **kwargs):
            full_kwargs = {}
            for k, a in kwargs.items():
                try:
                    full_kwargs[k] = ManParm.parse(a, md.mps)
                except Exception:
                    full_kwargs[k] = a
            
            eds, mps = self.mpmaps[kind]["func"](md.eds.get_new_name(),**full_kwargs)            
            md.eds.add(eds)
            md.mps.add(mps)
                        
        return partial(append_el, **all_kwargs)


    def create(self, maninfo, elmakers, **kwargs) -> ManDef:
        mps = self.mps.copy()
        for k, v in kwargs.items():
            if isinstance(v, ManParm):
                mps.add(v)
            elif isinstance(k, str):
                if k in mps.data:
                    mps[k].default=v
                else:
                    mps.add(ManParm.parse(v, mps, k))
        md = ManDef(maninfo, mps)
        for em in elmakers:
            if isinstance(em, int):
                if em == MBTags.CENTRE:
                    md.info.centre_loc = len(md.eds.data)
            else:
                em(md)
        md.mps = md.mps.remove_unused()
        return md
    

from flightanalysis.schedule.scoring import f3a

f3amb = ManoeuvreBuilder(
    ManParms([
        ManParm("speed", f3a.inter_speed, 30.0),
        ManParm("loop_radius", f3a.inter_radius, 55.0),
        ManParm("line_length", f3a.inter_length, 130.0),
        ManParm("point_length", f3a.inter_length, 20.0),
        ManParm("continuous_roll_rate", f3a.inter_roll_rate, np.pi/2),
        ManParm("partial_roll_rate", f3a.inter_roll_rate, np.pi/2),
        ManParm("full_roll_rate", f3a.inter_roll_rate, 3*np.pi/4),
        ManParm("snap_rate", f3a.inter_roll_rate, 4*np.pi),
        ManParm("stallturn_rate", f3a.inter_roll_rate, 2*np.pi),
        ManParm("spin_rate", f3a.inter_roll_rate, 1.7*np.pi),
        ManParm("ee_pause", f3a.inter_length, 20.0)
    ]),
    mpmaps=dict(
        line=dict(
            func=line,
            args=[],
            kwargs=dict(
                roll=0.0,
                speed="speed",
                length="line_length"
            )
        ),
        loop=dict(
            func=loop,
            args=["angle"],
            kwargs=dict(
                roll=0.0,
                ke=False,
                speed="speed",
                radius="loop_radius"   
            )
        ),
        roll=dict(
            func=roll_f3a,
            args=["rolls"],
            kwargs=dict(
                padded=True,
                reversible=True,
                speed="speed",
                line_length="line_length",
                partial_rate="partial_roll_rate",
                full_rate="full_roll_rate",
                pause_length="point_length",
            )    
        ),
        stallturn=dict(
            func=stallturn,
            args=[],
            kwargs=dict(
                speed=0.0,
                yaw_rate="stallturn_rate"   
            )
        ),
        snap=dict(
            func=snap,
            args=["rolls"],
            kwargs=dict(
                speed="speed",
                break_angle=np.radians(10),
                rate="snap_rate",
                break_rate=2*np.pi,
                line_length="line_length",
                padded=True
            )
        ),
        spin=dict(
            func=spin,
            args=["turns"],
            kwargs=dict(
                speed=10,
                break_angle=np.radians(30),
                rate="spin_rate",
                break_rate=6,
                reversible=True
            )
        )

    )
)