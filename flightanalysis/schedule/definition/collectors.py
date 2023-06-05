"""The collectors are serializable functions that return parameters from elements"""
from flightanalysis.base.collection import Collection
from . import Opp



class Collector(Opp):
    def __init__(self, elname, pname):
        self.pname = pname
        self.elname = elname
        super().__init__(f"{self.elname}.{self.pname}")

    def __call__(self, els):
        """return the value"""
        return els.get_parameter_from_element(self.elname, self.pname)

    def __str__(self):
        return self.name

    @staticmethod
    def parse(ins, coll: Collection):
        try:
            return Opp.parse(ins, coll)
        except KeyError:
            return Collector(*ins.strip(" ").split("."))

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
    
    def to_list(self):
        return [str(v) for v in self]
    
    @staticmethod
    def from_list(data):
        coll = Collectors()
        for d in data:
            coll.add(Collector.parse(d, coll))
        return coll
    