from . import Manoeuvre
from typing import List
from io import open
from json import load
from geometry import Point, Quaternion, Transformation
import numpy as np
from flightanalysis.section import Section

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

    @staticmethod
    def from_dict(val):
        return Schedule(
            val['name'],
            Categories.lookup[val['category']],
            val['entry'],
            val['entry_x_offset'],
            val['entry_z_offset'],
            [Manoeuvre.from_dict(manoeuvre) for manoeuvre in val['manoeuvres']]
        )

    @staticmethod
    def from_json(file: str):
        with open(file, "r") as f:
            return Schedule.from_dict(load(f))

    def create_template(self, enter_from: str, distance: float):
        box_scale = np.tan(np.radians(60)) * distance

        dmul = -1.0 if enter_from == "right" else 1.0
        ipos = Point(
            dmul * box_scale * self.entry_x_offset,
            distance,
            box_scale * self.entry_z_offset
        )

        iatt = Quaternion.from_euler(Point(np.pi, 0, 0))

        if self.entry == "inverted":
            iatt = Quaternion.from_euler(Point(0, np.pi, 0)) * iatt
        if enter_from == "left":
            iatt = Quaternion.from_euler(Point(0, 0, np.pi)) * iatt

        itrans = Transformation(ipos, iatt)

        mans = []
        #TODO add exit line on construction
        for manoeuvre in self.manoeuvres:
            itrans = manoeuvre.create_template(itrans, box_scale)
            
        self.template = Section.stack([man.section for man in mans])
        return itrans
