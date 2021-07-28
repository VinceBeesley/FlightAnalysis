from uuid import uuid4
from geometry import Transformation
from flightanalysis import Section
from flightanalysis.schedule.element import LoopEl, LineEl, StallTurnEl, SnapEl, SpinEl
from uuid import uuid4


class Manoeuvre():
    def __init__(self, name: str, k: float, elements: list, uid: str = None):
        self.name = name
        self.k = k
        self.elements = elements
        self._elm_lookup = {elm.uid: elm for elm in self.elements}
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

        template = Section.stack(templates)
        template.data["manoeuvre"] = self.uid
        return template

    def get_data(self, sec: Section):
        return Section(sec.data.loc[sec.data.manoeuvre == self.uid])

    def match_intention(self, transform: Transformation, flown: Section, speed: float):
        elms = []

        for elm in self.elements:
            elms.append(elm.match_intention(transform, elm.get_data(flown)))
            transform = elms[-1].create_template(
                transform, speed, True).get_state_from_index(-1).transform

        return self.replace_elms(elms), transform

    def get_elm_by_type(self, Elm):
        return [el for el in self.elements if el.__class__ == Elm]

    def replace_elms(self, elms):
        elm_search = {elm.uid: elm for elm in elms}
        return Manoeuvre(
            self.name, self.k,
            [elm_search[elm.uid] if elm.uid in elm_search.keys() else elm.set_parameter()
             for elm in self.elements],
            self.uid
        )

    def fix_loop_diameters(self):
        loops = self.get_elm_by_type(LoopEl)
        if len(loops) > 0:
            diameter = loops[0].diameter
            return self.replace_elms(
                [loop.set_parameter(diameter=diameter)
                 for loop in self.get_elm_by_type(LoopEl)]
            )
        else:
            return self.replace_elms([])
