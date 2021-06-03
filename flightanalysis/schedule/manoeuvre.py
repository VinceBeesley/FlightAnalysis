from . import Element
from typing import List
from uuid import uuid4

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



def element_maker(elements, x, z, direction, position="Centred"):
    """Take a simplified element definition and generate a scaled, positioned set of elements.
    
    Args:
        elements ([type]): [description]
        x ([type]): [description]
        y ([type]): [description]
        direction ([type]): [description]
        position (str, optional): [description]. Defaults to "Centred".
    """
    radius = 0.45
    rolllength = 0.4
    
    