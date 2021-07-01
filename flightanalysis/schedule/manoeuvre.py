from . import Element
from typing import List
from uuid import uuid4
from geometry import Transformation
from flightanalysis import Section
from uuid import uuid4

class Manoeuvre():
    def __init__(self, name: str, k: float, elements: List[Element]):
        self.name = name
        self.elements = elements
        self.k = k
        self.uid = uuid4()

    def create_template(self, transform: Transformation, scale: float ) -> Section: 
        itrans = transform
        #print("Manoeuvre : {}".format(manoeuvre.name))
        templates = []
        for i, element in enumerate(self.elements):
            templates.append(element.create_template(itrans, 30.0, scale))
            itrans = templates[-1].get_state_from_index(-1).transform
            #print("element {0}, {1}".format(element.classification, (itrans.translation / scale).to_list()))

        template =  Section.stack(templates)
        template.data["manoeuvre"] = self.uid
        
        return template

    def get_data(self, sec: Section):
        return Section(sec.data.loc[sec.data.manoeuvre==self.uid])
        