from . import Manoeuvre
from typing import List, Union, IO
from geometry import Point, Quaternion, Transformation, Euler, PX, PY, PZ
from flightanalysis.state import State
from flightanalysis.schedule.elements import get_rates, Line
import numpy as np
from flightanalysis.schedule.figure_rules import Categories


# TODO it would be better if the list index of each manoeuvre corresponded with the uid. This is not possible because takeoff is not included as a manoeuvre. 
# TODO perhaps include takeoff in the list as manoeuvre 0 and add it when reading from the json, use a constructor rather than __init__ when creating from python
# TODO this will cause a problem when creating templates, as some data must (probably) be created for the takeoff, which will bugger up the entry_x_offset and dtw alignment (if its a straight line)


class Schedule():
    def __init__(
        self,
        name: str,
        category: Categories,
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

        if all(isinstance(x, Manoeuvre) for x in manoeuvres):
            self.manoeuvres = manoeuvres
        elif all(isinstance(x, dict) for x in manoeuvres):
            self.manoeuvres = [Manoeuvre(**x) for x in manoeuvres]

    def to_dict(self):
        return dict(
            name=self.name,
            category=self.category.name,
            manoeuvres=[man.to_dict() for man in self.manoeuvres]
        )

    def replace_manoeuvres(self, new_mans: List[Manoeuvre]):
        """Replace all the manoeuvres
        """
        return Schedule(self.name, self.category, new_mans)

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
            [manoeuvre.scale(factor) for manoeuvre in self.manoeuvres]
        )

    def scale_distance(self, distance):
        return self.scale(np.tan(np.radians(60)) * distance)

    def create_template(self, itrans: Transformation, speed: float) -> State:
        """Create labelled template flight data

        Args:
            itrans (Transformation): transformation to initial position and orientation 
            speed (float): constant speed to use for the template flight, in m/s

        Returns:
            State: labelled template flight data
        """
        templates = []

        for i, manoeuvre in enumerate(self.manoeuvres):
            if i == len(self.manoeuvres) - 1: 
                speed = speed / 10
            templates.append(manoeuvre.create_template(itrans, speed))
            itrans = templates[-1][-1].transform

        return State.stack(templates)

    def match_intention(self, alinged: State):
        """resize every element of the schedule to best fit the corresponding element in a labelled State

        Args:
            alinged (State): labelled flight data

        Returns:
            Schedule: new schedule with all the elements resized
        """

        transform = Transformation(
            alinged[0].pos,
            alinged[0].att.closest_principal()
        )

        _mans = []
        for man in self.manoeuvres:
            man, transform = man.match_intention(
                transform, man.get_data(alinged), alinged.u.mean())
            _mans.append(man)

        return self.replace_manoeuvres(_mans)

    def correct_intention(self):
        return self.replace_manoeuvres([man.fix_intention() for man in self.manoeuvres])

    def create_matched_template(self, alinged: State) -> State:
        """This will go through all the manoeuvres in a labelled State and create a template with only the initial position and speed of each matched"""
        rates = get_rates(alinged)

        iatt = self.create_iatt(alinged[0].direction()[0])

        templates = []
        for manoeuvre in self.manoeuvres:
            transform = Transformation(
                manoeuvre.get_data(alinged)[0].pos,
                iatt
            )
            templates.append(manoeuvre.create_template(
                transform, rates["speed"]))
            iatt = templates[-1][-1].att

        return State.stack(templates)

    def create_elm_matched_template(self, alinged: State) -> State:
        """This will go through all the elements in a labelled State and create a template with the initial position and speed of each matched"""
        rates = get_rates(alinged)

        iatt = self.create_iatt(alinged[0].direction()[0])

        templates = []
        for manoeuvre in self.manoeuvres:
            mtemps = []
            for elm in manoeuvre.elements:
                transform = Transformation(
                    elm.get_data(alinged)[0].pos,
                    iatt
                )
                mtemps.append(elm.create_template(transform, rates["speed"]))
                iatt = mtemps[-1][-1].att
            
            templates.append(manoeuvre.label(State.stack(mtemps)))

        return State.stack(templates)

    def create_man_matched_template(self, alinged: State) -> State:
        """This will go through all the manoeuvres in a labelled State, measure the rates and return a scaled template for each based on the rates"""
        iatt = self.create_iatt(alinged[0].direction)
        templates = []
        for man in self.manoeuvres:
            flown = man.get_data(alinged)
            rates = get_rates(flown)
            transform = Transformation(
                flown[0].pos,
                iatt
            )
            templates.append(
                man.scale(rates["distance"] * np.tan(np.radians(60)))
                .create_template(transform, rates["speed"])
            )
            iatt = templates[-1][-1].att
        return templates

    def label_from_splitter(self, flown: State, splitter: list) -> State:
        """label the manoeuvres in a State based on the flight coach splitter information

        Args:
            flown (State): State read from the flight coach json
            splitter (list): the mans field of a flight coach json

        Returns:
            State: State with labelled manoeuvres
        """

        takeoff = flown.data.iloc[0:int(splitter[0]["stop"])+2]

        labelled = [State(takeoff).label(manoeuvre=0)]
        
        for split_man, man in zip(splitter[1:], self.manoeuvres):
            start, stop = int(split_man["start"]), int(split_man["stop"])
            labelled.append(man.label(State(flown.data.iloc[start:stop+2])))

        return State.stack(labelled)

    @staticmethod
    def get_takeoff(sec: State):
        return State(sec.data.loc[sec.data.manoeuvre == 0])

    def get_manoeuvre_data(self, sec: State, include_takeoff: bool = False) -> list:
        tsecs = []
        if include_takeoff:
            tsecs.append(Schedule.get_takeoff(sec))
        tsecs += self.get_data(sec, self.manoeuvres)
        return tsecs

    def get_data(self, sec: State, mans: List[Manoeuvre]) -> List[State]:
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

    def get_subset(self, sec: State, first_manoeuvre: int, last_manoeuvre: int):
        fmanid = self.manoeuvres[first_manoeuvre].uid
        if last_manoeuvre == -1 or last_manoeuvre >= len(self.manoeuvres):
            lmanid = self.manoeuvres[-1].uid + 1
        else:
            lmanid = self.manoeuvres[last_manoeuvre].uid


        return State(sec.data.loc[(sec.data.manoeuvre >= fmanid) & (sec.data.manoeuvre < lmanid)])