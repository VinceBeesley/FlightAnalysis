from . import Manoeuvre
from typing import List
from geometry import Point, Quaternion, Transformation, Points
from flightanalysis.section import Section
from flightanalysis.schedule.element import LoopEl, LineEl, SnapEl, SpinEl, StallTurnEl, get_rates
import numpy as np 


class Categories():
    F3A = 0
    IMAC = 1
    IAC = 2

    lookup = {
        "F3A": F3A,
        "IMAC": IMAC,
        "IAC": IAC
    }


class StartingPosition():
    def __init__(self, x_offset: float, z_offset: float, orientation: str):
        self.x_offset = x_offset
        self.z_offset = z_offset
        self.orientation = orientation


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
    
    def create_template(self, enter_from: str, speed:float, distance:float):
        """returns a section containing labelled template data 

        Args:
            enter_from (str): [description]
            distance (float): [description]

        Returns:
            [type]: [description]
        """
        dmul = -1.0 if enter_from == "right" else 1.0
        ipos = Point(
            dmul * self.entry_x_offset,
            distance,
            self.entry_z_offset
        )

        iatt = Quaternion.from_euler(Point(np.pi, 0, 0))

        if self.entry == "inverted":
            iatt = Quaternion.from_euler(Point(0, np.pi, 0)) * iatt
        if enter_from == "left":
            iatt = Quaternion.from_euler(Point(0, 0, np.pi)) * iatt

        itrans = Transformation(ipos, iatt)

        templates = []
        #TODO add exit line on construction
        for manoeuvre in self.manoeuvres:
            templates.append(manoeuvre.create_template(itrans, speed))
            itrans = templates[-1].get_state_from_index(-1).transform

        return Section.stack(templates)


    def match_rates(self, rates: dict):

        sec = self.scale_distance(rates["distance"])
        
        _mans = []
        for manoeuvre in sec.manoeuvres:
            _elms = []
            for element in manoeuvre.elements:
                _elms.append(element.match_axis_rate(rates[element.__class__], rates["speed"]))
            _mans.append(Manoeuvre(
                manoeuvre.name, manoeuvre.k, _elms
            ))
            _mans[-1].uid = manoeuvre.uid
        return Schedule(
            sec.name,
            sec.category,
            sec.entry,
            sec.entry_x_offset,
            sec.entry_z_offset,
            _mans
        )