from . import ManDef, ManInfo, ManParms
from flightanalysis import State
from typing import Dict
from geometry import Transformation
from flightanalysis import Schedule


class SchedDef:
    def __init__(self, name, mds: Dict[str, ManDef]=None):
        self.name = name
        self.mds = {} if mds is None else mds
    
    def __getitem__(self, key) -> ManDef:
        return list(self.mds.values())[key]

    def add(self, md: ManDef):
        self.mds[md.info.short_name] = md
        return md

    def add_new_manoeuvre(self, info: ManInfo, defaults=None):
        return self.add(ManDef(info,defaults))

    def create_schedule(self, depth: float, wind: float) -> Schedule:
        return Schedule(
            {name: m.create(depth, wind) for name, m in self.mds.items()}
        )      
    
    def create_template(self,depth:float=170, wind:int=-1):
        templates = []
        ipos = list(self.mds.values())[0].info.initial_position(depth,wind)
        
        mans = []
        for md in self.mds.values():

            itrans=Transformation(
                ipos if len(templates) == 0 else templates[-1][-1].pos,
                md.info.start.initial_rotation(wind)
            )
            man = md.create(itrans)
            templates.append(man.create_template(itrans))
            mans.append(man)
        return Schedule(mans), State.stack(templates)