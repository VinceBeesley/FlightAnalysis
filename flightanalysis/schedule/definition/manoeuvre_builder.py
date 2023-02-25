from . import ManDef, ManParm, ManParms, ElDef, ElDefs
from flightanalysis.schedule.elements import *
from typing import Dict, List
from numbers import Number
from functools import partial
from .element_builders import *
from numbers import Number


class ManoeuvreBuilder():
    def __init__(self, mps: ManParms, mpmaps:Dict[str, dict]):
        self.mps = mps
        self.mpmaps = mpmaps

    def __getattr__(self, name):
        if name in self.mpmaps:
            return partial(self.el, name)
    
    def base_parms(self, *kwargs):
        mps = self.mps.copy()  # this does not work
        for k,v in kwargs.items():
            if isinstance(v, Number):
                mps.data[k].default = v
            elif isinstance(v, ManParm):
                mps.data[k] = v
        return mps

    def el(self, kind, *args, **kwargs):
        #setup kwargs to pull defaults from mpmaps
        #returns a function that appends the created elements to a ManDef
        
        all_kwargs = {}
        for k, a, in self.mpmaps[kind]["kwargs"].items():
            all_kwargs[k] = a
        for k,a in kwargs.items():
            assert not k in self.mpmaps[kind]["args"]
            all_kwargs[k]=a
        for k, a in zip(self.mpmaps[kind]["args"], args):
            all_kwargs[k] = a
        
        def append_el(md: ManDef, func, **kwargs):
            full_kwargs = {}
            for k, a in kwargs.items():
                try:
                    full_kwargs[k] = ManParm.parse(a, md.mps)
                except Exception:
                    full_kwargs[k] = a
            
            eds, mps = self.mpmaps[kind]["func"](md.eds.get_new_name(),**full_kwargs)            
            md.eds.add(eds)
            md.mps.add(mps)
                        
        return partial(append_el, func=self.mpmaps[kind]["func"], **all_kwargs)


    def create(self, maninfo, elmakers, **kwargs):
        mps = self.mps.copy()
        for k, v in kwargs.items():
            if isinstance(v, ManParm):
                mps.add(v)
            elif k in mps.data:
                mps[k].default=v
        md = ManDef(maninfo, mps)
        for em in elmakers:
            em(md)
        return md
    


f3amb = ManoeuvreBuilder(
    ManParms([
        ManParm("speed", inter_f3a_speed, 30.0),
        ManParm("loop_radius", inter_f3a_radius, 55.0),
        ManParm("line_length", inter_f3a_length, 130.0),
        ManParm("point_length", inter_f3a_length, 10.0),
        ManParm("continuous_roll_rate", inter_f3a_roll_rate, np.pi/2),
        ManParm("partial_roll_rate", inter_f3a_roll_rate, np.pi/2),
        ManParm("full_roll_rate", inter_f3a_roll_rate, np.pi/2),
        ManParm("snap_rate", inter_f3a_roll_rate, 4*np.pi),
        ManParm("stallturn_rate", inter_f3a_roll_rate, 2*np.pi),
        ManParm("spin_rate", inter_f3a_roll_rate, 1.7*np.pi),
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
            func=StallTurn,
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
                break_rate=3*np.pi,
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