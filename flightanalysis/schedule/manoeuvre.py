from uuid import uuid4
from geometry import Transformation
from flightanalysis import Section
from uuid import uuid4

class Manoeuvre():
    def __init__(self, name: str, k: float, elements: list, uid: str = None):
        self.name = name
        self.k = k
        self.elements = elements
        if not uid:
            self.uid = str(uuid4())
        else:
            self.uid = uid

    def scale(self, factor: float):
        return Manoeuvre(
            self.name, 
            self.k,
            [elm.scale(factor) for elm in self.elements],
            self.uid
        )


    def create_template(self, transform: Transformation, speed: float) -> Section: 
        itrans = transform
        #print("Manoeuvre : {}".format(manoeuvre.name))
        templates = []
        for i, element in enumerate(self.elements):
            templates.append(element.create_template(itrans, speed))
            itrans = templates[-1].get_state_from_index(-1).transform
            #print("element {0}, {1}".format(element.classification, (itrans.translation / scale).to_list()))

        template =  Section.stack(templates)
        template.data["manoeuvre"] = self.uid
        return template

    def get_data(self, sec: Section):
        return Section(sec.data.loc[sec.data.manoeuvre==self.uid])
    
    def match_intention(self, transform: Transformation, flown: Section, speed: float):
        elms = []

        for elm in self.elements:           
            flown_elm = elm.get_data(flown)
            elm, transform = elm.match_intention(transform, flown_elm, speed)
            elms.append(elm)
            
        return Manoeuvre(
            self.name,
            self.k, 
            elms,
            self.uid
        ), transform
