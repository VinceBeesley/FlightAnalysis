from . import Manoeuvre
from typing import List
from geometry import Point, Quaternion, Transformation
from flightanalysis.section import Section
from flightanalysis.schedule.element import get_rates
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

    def replace_manoeuvres(self, new_mans):
        return Schedule(self.name, self.category, self.entry, self.entry_x_offset, self.entry_z_offset, new_mans)

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
            iatt = Quaternion.from_euler(Point(0, 0, np.pi)) * iatt
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
            self.create_itransform(-1.0 if enter_from ==
                                   "right" else 1.0, distance),
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
        return self.replace_manoeuvres(_mans)

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

        return self.replace_manoeuvres(_mans)

    def correct_intention(self):
        _mans = []
        for man in self.manoeuvres:
            _mans.append(man.fix_intention())
        return self.replace_manoeuvres(_mans)

    def create_matched_template(self, alinged: Section) -> Section:
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

    def label_from_splitter(self, flown: Section, splitter: list) -> Section:
        """label the manoeuvres in a section based on the flight coach splitter information

        Args:
            flown (Section): Section read from the flight coach json
            splitter (list): the mans field of a flight coach json

        Returns:
            Section: section with labelled manoeuvres
        """

        takeoff = flown.data.iloc[0:int(splitter[0]["stop"])+1]
        takeoff.loc[:,"manoeuvre"] = "takeoff"
        labelled = [Section(takeoff)]
        for split_man, man in zip(splitter[1:], self.manoeuvres):
            start, stop = int(split_man["start"]), int(split_man["stop"])
            labelled.append(man.label(Section(flown.data.iloc[start:stop+1])))
            
        return Section.stack(labelled)

    def get_manoeuvre_data(self, sec: Section, include_takeoff: bool = False) -> list:
        tsecs = []
        if include_takeoff:
            tsecs.append(Section(sec.data.loc[sec.data.manoeuvre == "takeoff"]))        
        tsecs += self.get_data(sec, self.manoeuvres)
        return tsecs

    def get_data(self, sec: Section, mans: List[Manoeuvre]) -> List[Section]:
        return [man.get_data(sec) for man in mans]

    def share_seperators(self, undo=False):
        """share each manoeuvres entry line with the preceding manoeuvre"""
        if undo:
            meth = "unshare_seperator"
        else:
            meth = "share_seperator"

        consec_mans = zip(self.manoeuvres[:-1], self.manoeuvres[1:])
        nmans = [getattr(man, meth)(nextman) for man, nextman in consec_mans]
        nmans.append(self.manoeuvres[-1].replace_elms([]))
        return self.replace_manoeuvres(nmans)

