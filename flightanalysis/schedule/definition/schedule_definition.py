from . import ManDef, ManInfo, ManParms
from typing import Dict

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
    

