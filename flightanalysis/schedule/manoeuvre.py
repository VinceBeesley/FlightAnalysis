from . import Element
from typing import List
from uuid import uuid4
from geometry import Transformation
from flightanalysis import Section

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

    def create_template(self, transform: Transformation, scale: float = 200.0 ): 
        itrans = transform
        #print("Manoeuvre : {}".format(manoeuvre.name))
        
        for i, element in enumerate(self.elements):
            itrans = element.create_template(itrans, element, 50.0, scale)
            #print("element {0}, {1}".format(element.classification, (itrans.translation / scale).to_list()))

        self.template = Section.stack([elm.template for elm in self.elements])
        return itrans

