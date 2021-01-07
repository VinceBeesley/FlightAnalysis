from . import Element
from typing import List


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