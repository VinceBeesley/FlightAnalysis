"""The collectors are serializable functions that return parameters from elements"""
from flightanalysis.base.collection import Collection
from flightanalysis.state import State
from . import Opp
from uuid import uuid1



class Collector(Opp):
    def __init__(self, elname, pname):
        self.pname = pname
        self.elname = elname
        super().__init__(f"{self.elname}.{self.pname}")

    def __call__(self, els, flown: State, template:State):
        """return the value"""        
        return getattr(els.data[self.elname], self.pname)#(tp[0].transform, fl))[0]
        # todo think about visibility here.
    def __str__(self):
        return self.name

    @staticmethod
    def parse(ins, name=None):
        return Opp.parse_f(
            ins, 
            lambda ins : Collector(*ins.strip(" ").split(".")),
            uuid1() if name is None else name
        )
        
    def to_dict(self):
        return dict(
            elname=self.elname,
            pname=self.pname
        )

    def copy(self):
        return Collector(self.elname, self.pname)


class Collectors(Collection):
    VType=Opp
    uid="name"

    def __str__(self):
        return str([str(v) for v in self])
    
    @staticmethod
    def parse(ins: str):
        return Collectors([Collector.parse(s) for s in ins[1:-1].split(",")])

    @staticmethod
    def from_eldef(el):
        return Collectors([Collector(el.name, pname) for pname in el.Kind.parameters])
    
    def to_dict(self):
        return {v.name: str(v) for v in self}

    @staticmethod
    def from_dict(data):
        return Collectors({k: Collector.parse(v, k) for k, v in data.items()})

    def to_list(self):
        return [str(v) for v in self]
    
    @staticmethod
    def from_list(data):
        coll = Collectors()
        for d in data:
            coll.add(Collector.parse(d))
        return coll
    
    def keys(self):
        return [c.elname for c in self]
    

    