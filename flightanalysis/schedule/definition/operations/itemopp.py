
from __future__ import annotations
from numbers import Number
from flightanalysis.base.collection import Collection
from uuid import uuid1
from ast import literal_eval
from dataclasses import dataclass, field
from typing import Any
from .operation import Opp
from .funopp import FunOpp



@dataclass
class ItemOpp(Opp):
    """This class creates an Operation that returns a single item from a combination ManParm"""
    a: Any
    item: int
    
    def __call__(self, mps):
        return self.a.valuefunc(self.item)(mps)
    
    def __str__(self):
        return f"{self.a.name}[{self.item}]"

    @staticmethod
    def parse_f(inp: str, parser, name:str=None):
        contents = inp.split("[")
        if not len(contents) == 2:
            raise ValueError
        return ItemOpp(
            name,
            Opp.parse_f(contents[0], parser, name), 
            int(contents[1][:-1])
        )

    @staticmethod
    def parse(inp: str, coll: Collection, name:str=None):
        contents = inp.split("[")
        if not len(contents) == 2:
            raise ValueError
        return ItemOpp(
            name,
            coll.VType.parse(contents[0], coll), 
            int(contents[1][:-1])
        )

    def __abs__(self):
        return FunOpp(self.name, self, "abs")
