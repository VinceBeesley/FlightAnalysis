from flightdata import Flight
from typing import List


class Categories():
    F3A = 0
    IMAC = 1
    IAC = 2

    lookup = {
        "F3A": F3A,
        "IMAC": IMAC,
        "IAC": IAC
    }


class Elements():
    LOOP = 0
    LINE = 1
    ROLL = 2
    SPIN = 3
    STALLTURN = 4
    SNAP = 5

    lookup = {
        "loop": LOOP,
        "line": LINE,
        "roll": ROLL,
        "spin": SPIN,
        "stallturn": STALLTURN,
        "snap": SNAP
    }


class Element():
    def __init__(self, classification: int, proportion: float):
        self.classification = classification
        self.proportion = proportion

    def from_dict(val):
        return Element(Elements.lookup[val["classification"]], val["proportion"])


class Manoeuvre():
    def __init__(self, name: str, k: float, elements: List[Element]):
        self.name = name
        self.elements = elements
        self.k = k

    @staticmethod
    def from_dict(val):
        return Manoeuvre(
            val['name'],
            val['k'],
            [Element.from_dict(element) for element in val['elements']]
        )


class Schedule():
    def __init__(self, name: str, category: int, entry: str, manoeuvres: List[Manoeuvre]):
        self.name = name
        self.category = category
        self.entry = entry
        self.manoeuvres = manoeuvres

    @staticmethod
    def from_dict(val):
        return Schedule(
            val['name'],
            Categories.lookup[val['category']],
            val['entry'],
            [Manoeuvre.from_dict(manoeuvre) for manoeuvre in val['manoeuvres']]
        )
