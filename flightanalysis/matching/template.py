

from flightanalysis.schedule import Schedule, Manoeuvre, Element, ElClass, Categories
from flightanalysis.section import Section
from typing import Union, Dict, List
from geometry import Point, Quaternion, Transformation
import numpy as np


class MatchedSection(object):
    def __init__(
        self,
        definition: Union[Schedule, Manoeuvre, Element],
        template: Section,
        subelements: list = None,
        flown: Section = None
    ):
        self.definition = definition
        self.template = template
        self.subelements = subelements
        self.flown = flown

    @staticmethod
    def from_schedule(schedule: Schedule, enter_from: str, distance):
        box_scale = np.tan(np.radians(60)) * distance

        dmul = -1.0 if enter_from == "right" else 1.0
        ipos = Point(
            dmul * box_scale * schedule.entry_x_offset,
            distance,
            box_scale * schedule.entry_z_offset
        )

        iatt = Quaternion.from_euler(Point(np.pi, 0, 0))

        if schedule.entry == "inverted":
            iatt = Quaternion.from_euler(Point(0, np.pi, 0)) * iatt
        if enter_from == "left":
            iatt = Quaternion.from_euler(Point(0, 0, np.pi)) * iatt

        itrans = Transformation(ipos, iatt)

        elms = []
        for manoeuvre in schedule.manoeuvres:
            elms += MatchedSection.from_manoeuvre(
                itrans, manoeuvre, scale=box_scale)
            itrans = elms[-1].get_state_from_index(-1).transform

        elms.append(MatchedSection.from_element(
            itrans,
            Element(ElClass.LINE, 0.25, 0.0, 0.0), 30.0, box_scale)
        )  # add an exit line

        return MatchedSection(
            schedule,
            Section.stack([elm.template for elm in elms]),
            elms,
            None
        )

    @staticmethod
    def from_manoeuvre(transform: Transformation, manoeuvre: Manoeuvre, scale: float = 200.0):
        elms = []
        itrans = transform
        #print("Manoeuvre : {}".format(manoeuvre.name))
        for i, element in enumerate(manoeuvre.elements):
            elm = Section.from_element(itrans, element, 50.0, scale)

            elms.append(MatchedSection(element, elm, None, None))
            itrans = elm.get_state_from_index(-1).transform
            #print("element {0}, {1}".format(element.classification, (itrans.translation / scale).to_list()))

        return MatchedSection(
            manoeuvre,
            Section.stack([elm.template for elm in elms]),
        )


class ElementTemplate:
    def __init__(self, template):
        self.template = template

class ManoeuvreTemplate(Manoeuvre):
    def __init__(self, template: Section, elements: List[ElementTemplate] ):
        self.template = template
        self.elements = elements

    def __getitem__(self, id):
        return self.elements[id]


class ScheduleTemplate:
    def __init__(self, template: Section, manoeuvres: Dict[ManoeuvreTemplate]):
        self.template = template
        self.manoeuvres = manoeuvres

    def __getattr__(self, name):
        return self.manoeuvres[name]

    @staticmethod
    def from_schedule(schedule: Schedule, enter_from: str, distance):
        box_scale = np.tan(np.radians(60)) * distance

        dmul = -1.0 if enter_from == "right" else 1.0
        ipos = Point(
            dmul * box_scale * schedule.entry_x_offset,
            distance,
            box_scale * schedule.entry_z_offset
        )

        iatt = Quaternion.from_euler(Point(np.pi, 0, 0))

        if schedule.entry == "inverted":
            iatt = Quaternion.from_euler(Point(0, np.pi, 0)) * iatt
        if enter_from == "left":
            iatt = Quaternion.from_euler(Point(0, 0, np.pi)) * iatt

        itrans = Transformation(ipos, iatt)

        mans = []
        for manoeuvre in schedule.manoeuvres:
            mans += ManoeuvreTemplate.from_manoeuvre(
                itrans, manoeuvre, scale=box_scale)
            itrans = mans[-1].get_state_from_index(-1).transform

#        TODO make Takeoff and landing manoeuvre
#        mans.append(MatchedSection.from_element(
#            itrans,
#            Element(ElClass.LINE, 0.25, 0.0, 0.0), 30.0, box_scale)
#        )  # add an exit line

        return ScheduleTemplate(
            schedule.name,
            schedule.category,
            schedule.entry,
            schedule.en
            Section.stack([elm.template for elm in mans]),
            mans,
            None
        )

