from . import Manoeuvre
from typing import List
from geometry import Point, Quaternion, Transformation, Points
from flightanalysis.section import Section
from flightanalysis.schedule.element import LoopEl, LineEl, SnapEl, SpinEl, StallTurnEl, get_rates
import numpy as np


class Schedule():
    def __init__(
        self,
        name: str,
        category: int,
        entry: str,
        entry_x_offset: float,
        entry_z_offset: float,
        manoeuvres: List[Manoeuvre]
    ):
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

    def scale(self, box_scale):
        return Schedule(
            self.name,
            self.category,
            self.entry,
            self.entry_x_offset * box_scale,
            self.entry_z_offset * box_scale,
            [manoeuvre.scale(box_scale) for manoeuvre in self.manoeuvres]
        )

    def scale_distance(self, distance):
        return self.scale(np.tan(np.radians(60)) * distance)

    def create_iatt(self, direction):
        iatt = Quaternion.from_euler(Point(np.pi, 0, 0))
        if self.entry == "inverted":
            iatt = Quaternion.from_euler(Point(0, np.pi, 0)) * iatt
        if direction == "right":
            iatt= Quaternion.from_euler(Point(0, 0, np.pi)) * iatt
        return iatt

    def create_itransform(self, direction, distance):
        dmul = 1 if direction == "right" else -1
        return Transformation(
            Point(
                self.entry_x_offset * dmul,
                distance,
                self.entry_z_offset
            ),
            self.create_iatt(direction)
        )

    def create_template(self, itrans: Transformation, speed: float):
        templates = []
        # TODO add exit line on construction
        for manoeuvre in self.manoeuvres:
            print(manoeuvre.name)
            templates.append(manoeuvre.create_template(itrans, speed))
            itrans = templates[-1].get_state_from_index(-1).transform

        return Section.stack(templates)

    def create_raw_template(self, enter_from: str, speed: float, distance: float):
        """returns a section containing labelled template data 

        Args:
            enter_from (str): [description]
            distance (float): [description]

        Returns:
            [type]: [description]
        """

        return self.create_template(
            self.create_itransform(-1.0 if enter_from == "right" else 1.0,distance),
            speed
        )

    def match_rates(self, rates: dict):

        sec = self.scale_distance(rates["distance"])

        _mans = []
        for manoeuvre in sec.manoeuvres:
            _elms = []
            for element in manoeuvre.elements:
                _elms.append(element.match_axis_rate(
                    rates[element.__class__], rates["speed"]))
            _mans.append(manoeuvre.replace_elms(_elms))
        return Schedule(sec.name, sec.category, sec.entry, sec.entry_x_offset, sec.entry_z_offset, _mans)

    def match_intention(self, alinged: Section):
        rates = get_rates(alinged)

        transform = self.create_itransform(
            -np.sign(alinged.get_state_from_index(0).transform.point(Point(1, 0, 0)).x),
            rates["distance"]
        )

        _mans = []
        for man in self.manoeuvres:
            man, transform = man.match_intention(
                transform, man.get_data(alinged), rates["speed"])
            _mans.append(man)

        return Schedule(self.name, self.category, self.entry, self.entry_x_offset, self.entry_z_offset, _mans)

    def correct_intention(self):
        _mans = []
        for man in self.manoeuvres:
            #TODO add some checking logic here
            _mans.append(man.fix_intention())
        return Schedule(self.name, self.category, self.entry, self.entry_x_offset, self.entry_z_offset, _mans)


    def create_matched_template(self, alinged: Section):
        rates = get_rates(alinged)
    
        iatt = self.create_iatt(alinged.get_state_from_index(0).direction)

        templates = []
        for manoeuvre in self.manoeuvres:
            transform = Transformation(
                manoeuvre.get_data(alinged).get_state_from_index(0).pos,
                iatt
            )
            templates.append(manoeuvre.create_template(
                transform, rates["speed"]))
            iatt = templates[-1].get_state_from_index(-1).att

        return Section.stack(templates)
