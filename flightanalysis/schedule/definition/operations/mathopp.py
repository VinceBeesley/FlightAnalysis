from __future__ import annotations
from numbers import Number
from flightanalysis.base.collection import Collection
from uuid import uuid1
from ast import literal_eval
from dataclasses import dataclass, field
from typing import Any
from .operation import Opp


@dataclass
class MathOpp(Opp):
    """This class facilitates various ManParm opperations and their serialisation"""
    opps = ["+", "-", "*", "/"]
    a: Any
    b: Any
    opp: str

    def __call__(self, mps, **kwargs):
        if self.opp == "+":
            return self.get_vf(self.a)(mps, **kwargs) + self.get_vf(self.b)(mps, **kwargs)
        elif self.opp == "-":
            return self.get_vf(self.a)(mps, **kwargs) - self.get_vf(self.b)(mps, **kwargs)
        elif self.opp == "*":
            return self.get_vf(self.a)(mps, **kwargs) * self.get_vf(self.b)(mps, **kwargs)
        elif self.opp == "/":
            return self.get_vf(self.a)(mps, **kwargs) / self.get_vf(self.b)(mps, **kwargs)

    def __str__(self):
        return f"({str(self.a)}{self.opp}{str(self.b)})"

    @staticmethod
    def parse_f(inp:str, parser, name:str=None):
        if inp[0] == "(" and inp[-1] == ")":
            bcount = 0
            for i, l in enumerate(inp):
                bcount += 1 if l=="(" else 0
                bcount -=1 if l==")" else 0
            
                if bcount == 1 and l in MathOpp.opps:
                    return MathOpp(
                        name,
                        Opp.parse_f(inp[1:i], parser, name),
                        Opp.parse_f(inp[i+1:-1], parser, name),
                        l
                    )
                    
        raise ValueError(f"cannot read an MathOpp from the outside of {inp}")

    @staticmethod
    def parse(inp:str, coll: Collection, name:str=None):
        if inp[0] == "(" and inp[-1] == ")":
            bcount = 0
            for i, l in enumerate(inp):
                bcount += 1 if l=="(" else 0
                bcount -=1 if l==")" else 0
            
                if bcount == 1 and l in MathOpp.opps:
                    return MathOpp(
                        name,
                        coll.VType.parse(inp[1:i], coll),
                        coll.VType.parse(inp[i+1:-1], coll),
                        l
                    )
                    
        raise ValueError(f"cannot read an MathOpp from the outside of {inp}")


    def list_parms(self) -> list[str]:
        parms = []
        if isinstance(self.a, Opp):
            parms = parms + self.a.list_parms()
        if isinstance(self.b, Opp):
            parms = parms + self.b.list_parms()
        return parms