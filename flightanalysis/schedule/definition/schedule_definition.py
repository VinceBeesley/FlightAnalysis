from . import ManDef, ManInfo, ManParms
from flightanalysis import State
from typing import Dict
from geometry import Transformation

class SchedDef:
    def __init__(self, name, mds: Dict[str, ManDef]=None):
        self.name = name
        self.mds = {} if mds is None else mds
    
    def add(self, md: ManDef):
        self.mds[md.info.short_name] = md
        return md

    def add_new_manoeuvre(self, info: ManInfo, defaults=None):
        return self.add(ManDef(
            info,
            defaults=ManParms.create_defaults_f3a() if defaults is None else defaults
        ))
    

    def create_template(self):
        templates = []
        wind=1
        itrans = list(self.mds.values())[0].info.initial_transform(170,wind)
        ipos = itrans.translation
        for md in self.mds.values():
            itrans=Transformation(ipos, md.info.start.initial_rotation(wind))
            templates.append(md.create_entry_line(itrans)(md.mps).create_template(itrans))
            itrans=templates[-1][-1].transform
            templates.append(md.create().create_template(itrans))
            ipos=templates[-1][-1].pos#, md.info.start.initial_rotation(wind))

        return State.stack(templates)