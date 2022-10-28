"""The collectors are serializable functions that return parameters from elements"""
from flightanalysis.base.collection import Collection


class Collector:
    def __init__(self, elname, pname):
        self.pname = pname
        self.elname = elname
    
    def __call__(self, els):
        """return the value"""
        return els.get_parameter_from_element(self.elname, self.pname)

    def __str__(self):
        return f"{self.elname}.{self.pname}"

    @staticmethod
    def parse(ins):
        return Collector(*ins.strip(" ").split("."))


class Collectors(Collection):
    VType=Collector
    uid="pname"

    def __str__(self):
        return str([str(v) for v in self])
    
    @staticmethod
    def parse(ins: str):
        return Collectors([Collector.parse(s) for s in ins[1:-1].split(",")])

    @staticmethod
    def from_eldef(el):
        return Collectors([Collector(el.name, pname) for pname in el.Kind.parameters])
    
