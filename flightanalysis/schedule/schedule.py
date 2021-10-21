from . import Manoeuvre
from typing import List, Union, IO
from geometry import Point, Quaternion, Transformation
from flightanalysis.section import Section
from flightanalysis.schedule.element import get_rates
import numpy as np
from flightanalysis.schedule.figure_rules import Categories
from json import loads, load, dumps


# TODO it would be better if the list index of each manoeuvre corresponded with the uid. This is not possible because takeoff is not included as a manoeuvre. 
# TODO perhaps include takeoff in the list as manoeuvre 0 and add it when reading from the json, use a constructor rather than __init__ when creating from python
# TODO this will cause a problem when creating templates, as some data must (probably) be created for the takeoff, which will bugger up the entry_x_offset and dtw alignment (if its a straight line)

class Schedule():
    def __init__(
        self,
        name: str,
        category: Categories,
        entry: str,
        entry_x_offset: float,
        entry_z_offset: float,
        manoeuvres: List[Manoeuvre]
    ):
        """
        Args:
            name (str): [description]
            category (Categories): F3A, IMAC, IAC
            entry (str): upright or inverted
            entry_x_offset (float): x starting position, when flown left to right. 
                                    will be reversed when creating right to left templates
            entry_z_offset (float): z starting position
            manoeuvres (List[Manoeuvre]): [description]
        """
        self.name = name

        if isinstance(category, Categories):
            self.category = category
        elif isinstance(category, str):
            self.category = Categories[category]

        self.entry = entry
        self.entry_x_offset = entry_x_offset
        self.entry_z_offset = entry_z_offset
        if all(isinstance(x, Manoeuvre) for x in manoeuvres):
            self.manoeuvres = manoeuvres
        elif all(isinstance(x, dict) for x in manoeuvres):
            self.manoeuvres = [Manoeuvre(**x) for x in manoeuvres]

    def to_dict(self):
        return dict(
            name=self.name,
            category=self.category.name,
            entry=self.entry,
            entry_x_offset=self.entry_x_offset,
            entry_z_offset=self.entry_z_offset,
            manoeuvres=[man.to_dict() for man in self.manoeuvres]
        )

    def manoeuvre(self, name):
        for manoeuvre in self.manoeuvres:
            if manoeuvre.name == name:
                return manoeuvre
        raise KeyError()

    def replace_manoeuvres(self, new_mans: List[Manoeuvre]):
        """Replace all the manoeuvres
        """
        return Schedule(self.name, self.category, self.entry, self.entry_x_offset, self.entry_z_offset, new_mans)

    def scale(self, factor: float):
        """Scale the schedule by a factor

        Args:
            factor (float)

        Returns:
            Schedule: scaled schedule
        """
        return Schedule(
            self.name,
            self.category,
            self.entry,
            self.entry_x_offset * factor,
            self.entry_z_offset * factor,
            [manoeuvre.scale(factor) for manoeuvre in self.manoeuvres]
        )

    def scale_distance(self, distance):
        return self.scale(np.tan(np.radians(60)) * distance)

    def create_iatt(self, direction: str) -> Quaternion:
        """Create the initial orientation for a template

        Args:
            direction (str): "left" or "right" direction in (x axis) of velocity vector, +ve for right

        Returns:
            Quaternion: rotation to initial attitude
        """
        iatt = Quaternion.from_euler(Point(np.pi, 0, 0))
        if self.entry == "inverted":
            iatt = Quaternion.from_euler(Point(np.pi, 0, 0)) * iatt
        if direction == "left":
            iatt = Quaternion.from_euler(Point(0, 0, np.pi)) * iatt
        return iatt

    def create_itransform(self, direction: str, distance: float) -> Transformation:
        """create the initial transformation for a template

        Args:
            direction (str): "left" or "right" direction in (x axis) of velocity vector, +ve for right
            distance (float): distance from pilot position (y axis)

        Returns:
            Transformation: transformation to initial position and attitude
        """
        dmul = 1 if direction == "right" else -1
        return Transformation(
            Point(
                self.entry_x_offset * dmul,
                distance,
                self.entry_z_offset
            ),
            self.create_iatt(direction)
        )

    def create_template(self, itrans: Transformation, speed: float) -> Section:
        """Create labelled template flight data

        Args:
            itrans (Transformation): transformation to initial position and orientation 
            speed (float): constant speed to use for the template flight, in m/s

        Returns:
            Section: labelled template flight data
        """
        templates = []
        # TODO add exit line on construction
        for manoeuvre in self.manoeuvres:
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

        return self.create_template(self.create_itransform(enter_from, distance), speed)

    def match_rates(self, rates: dict):
        """Perform some measurements on a section and roughly scale the schedule to match

        Args:
            aligned (Section): flight data

        Returns:
            Schedule: scaled so that the axis rates roughly match the flight
        """
        sec = self.scale_distance(rates["distance"])
        return self.replace_manoeuvres([man.match_rates(rates) for man in sec.manoeuvres])

    def match_manoeuvre_rates(self, aligned: Section):
        """Perform some measurements on a section and roughly scale the schedule to match

        Args:
            aligned (Section): flight data with manoeuvre labels

        Returns:
            Schedule: scaled so that the axis rates roughly match the flight per manoeuvre
        """
        nmans = []
        for man in self.manoeuvres:
            rates = get_rates(man.get_data(aligned))
            nmans.append(man.match_rates(rates))
        return self.replace_manoeuvres(nmans)

    def match_intention(self, alinged: Section):
        """resize every element of the schedule to best fit the corresponding element in a labelled section

        Args:
            alinged (Section): labelled flight data

        Returns:
            Schedule: new schedule with all the elements resized
        """
        rates = get_rates(alinged)

        transform = self.create_itransform(
            alinged.get_state_from_index(0).direction,
            rates["distance"]
        )

        _mans = []
        for man in self.manoeuvres:
            man, transform = man.match_intention(
                transform, man.get_data(alinged), rates["speed"])
            _mans.append(man)

        return self.replace_manoeuvres(_mans)

    def correct_intention(self):
        return self.replace_manoeuvres([man.fix_intention() for man in self.manoeuvres])

    def create_matched_template(self, alinged: Section) -> Section:
        """This will go through all the manoeuvres in a labelled section and create a template with only the initial position and speed of each matched"""
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

    def create_elm_matched_template(self, alinged: Section) -> Section:
        """This will go through all the elements in a labelled section and create a template with the initial position and speed of each matched"""
        rates = get_rates(alinged)

        iatt = self.create_iatt(alinged.get_state_from_index(0).direction)

        templates = []
        for manoeuvre in self.manoeuvres:
            mtemps = []
            for elm in manoeuvre.elements:
                transform = Transformation(
                    elm.get_data(alinged).get_state_from_index(0).pos,
                    iatt
                )
                mtemps.append(elm.create_template(transform, rates["speed"]))
                iatt = mtemps[-1].get_state_from_index(-1).att
            
            templates.append(manoeuvre.label(Section.stack(mtemps)))

        return Section.stack(templates)

    def create_man_matched_template(self, alinged: Section) -> Section:
        """This will go through all the manoeuvres in a labelled section, measure the rates and return a scaled template for each based on the rates"""
        iatt = self.create_iatt(alinged.get_state_from_index(0).direction)
        templates = []
        for man in self.manoeuvres:
            flown = man.get_data(alinged)
            rates = get_rates(flown)
            transform = Transformation(
                flown.get_state_from_index(0).pos,
                iatt
            )
            templates.append(
                man.scale(rates["distance"] * np.tan(np.radians(60)))
                .create_template(transform, 1.5*rates["speed"])
            )
            iatt = templates[-1].get_state_from_index(-1).att
        return templates

    def label_from_splitter(self, flown: Section, splitter: list) -> Section:
        """label the manoeuvres in a section based on the flight coach splitter information

        Args:
            flown (Section): Section read from the flight coach json
            splitter (list): the mans field of a flight coach json

        Returns:
            Section: section with labelled manoeuvres
        """

        takeoff = flown.data.iloc[0:int(splitter[0]["stop"])+2]
        takeoff.loc[:, "manoeuvre"] = 0
        labelled = [Section(takeoff)]
        for split_man, man in zip(splitter[1:], self.manoeuvres):
            start, stop = int(split_man["start"]), int(split_man["stop"])
            labelled.append(man.label(Section(flown.data.iloc[start:stop+2])))

        return Section.stack(labelled)

    @staticmethod
    def get_takeoff(sec: Section):
        return Section(sec.data.loc[sec.data.manoeuvre == 0])

    def get_manoeuvre_data(self, sec: Section, include_takeoff: bool = False) -> list:
        tsecs = []
        if include_takeoff:
            tsecs.append(Schedule.get_takeoff(sec))
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

    def get_subset(self, sec: Section, first_manoeuvre: int, last_manoeuvre: int):
        fmanid = self.manoeuvres[first_manoeuvre].uid
        if last_manoeuvre == -1 or last_manoeuvre >= len(self.data.manoeuvres):
            lmanid = self.data.manoeuvres[-1].uid + 1
        else:
            lmanid = self.manoeuvres[last_manoeuvre].uid

        return Section(sec.data.loc[sec.data.manoeuvre >= fmanid and sec.data.manoeuvre < lmanid])