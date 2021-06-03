from . import Manoeuvre
from typing import List
from io import open
from json import load

class Categories():
    F3A = 0
    IMAC = 1
    IAC = 2

    lookup = {
        "F3A": F3A,
        "IMAC": IMAC,
        "IAC": IAC
    }


class Schedule():
    def __init__(self, name: str, category: int, entry: str, entry_x_offset:float, entry_z_offset: float, manoeuvres: List[Manoeuvre]):
        self.name = name
        self.category = category
        self.entry = entry
        self.entry_x_offset = entry_x_offset
        self.entry_z_offset = entry_z_offset
        self.manoeuvres = manoeuvres

    def manoeuvre(self, name):
        for manoeuvre in self.manoeuvres:
            if manoeuvre.name == name:
                return manoeuvre
        raise KeyError()

    @staticmethod
    def from_dict(val):
        return Schedule(
            val['name'],
            Categories.lookup[val['category']],
            val['entry'],
            val['entry_x_offset'],
            val['entry_z_offset'],
            [Manoeuvre.from_dict(manoeuvre) for manoeuvre in val['manoeuvres']]
        )

    @staticmethod
    def from_json(file: str):
        with open(file, "r") as f:
            return Schedule.from_dict(load(f))


