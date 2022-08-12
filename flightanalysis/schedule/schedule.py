from . import Manoeuvre
from typing import List, Dict
from geometry import Point, Quaternion, Transformation, Euler, PX, PY, PZ
from flightanalysis.state import State
from flightanalysis.schedule.elements import get_rates, Line
import numpy as np
from flightanalysis.schedule.figure_rules import Categories
from flightanalysis.base.collection import Collection

# TODO it would be better if the list index of each manoeuvre corresponded with the uid. This is not possible because takeoff is not included as a manoeuvre. 
# TODO perhaps include takeoff in the list as manoeuvre 0 and add it when reading from the json, use a constructor rather than __init__ when creating from python
# TODO this will cause a problem when creating templates, as some data must (probably) be created for the takeoff, which will bugger up the entry_x_offset and dtw alignment (if its a straight line)


class Schedule(Collection):
    VType = Manoeuvre

    def create_template(self, itrans: Transformation) -> State:
        """Create labelled template flight data
        Args:
            itrans (Transformation): transformation to initial position and orientation 
        Returns:
            State: labelled template flight data
        """
        templates = []

        for manoeuvre in self:
            itrans = itrans if len(templates) ==0 else templates[-1][-1].transform
            templates.append(manoeuvre.create_template(itrans))
            
        return State.stack(templates)

    def match_intention(self, itrans:Transformation, alinged: State):
        """resize every element of the schedule to best fit the corresponding element in a labelled State

        Args:
            alinged (State): labelled flight data

        Returns:
            Schedule: new schedule with all the elements resized
        """
        _mans = []
        for i, man in enumerate(self):
            man, transform = man.match_intention(
                transform if i>0 else Transformation(alinged[0].pos,itrans.att), 
                man.get_data(alinged)
            )
            _mans.append(man)

        return Schedule(_mans)

    def correct_intention(self):
        return self.replace_manoeuvres([man.fix_intention() for man in self])

    def create_matched_template(self, alinged: State) -> State:
        """This will go through all the manoeuvres in a labelled State and create a template with
         only the initial position and speed of each matched"""
        rates = get_rates(alinged)

        iatt = self.create_iatt(alinged[0].direction()[0])

        templates = []
        for manoeuvre in self:
            transform = Transformation(
                manoeuvre.get_data(alinged)[0].pos,
                iatt
            )
            templates.append(manoeuvre.create_template(
                transform, rates["speed"]))
            iatt = templates[-1][-1].att

        return State.stack(templates)

    def create_elm_matched_template(self, alinged: State) -> State:
        """This will go through all the elements in a labelled State and create a template 
        with the initial position and speed of each matched"""
        rates = get_rates(alinged)

        iatt = self.create_iatt(alinged[0].direction()[0])

        templates = []
        for manoeuvre in self:
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
        """This will go through all the manoeuvres in a labelled State,
        measure the rates and return a scaled template for each based on the rates"""
        iatt = self.create_iatt(alinged[0].direction)
        templates = []
        for man in self:
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
        
        for split_man, man in zip(splitter[1:], self):
            start, stop = int(split_man["start"]), int(split_man["stop"])
            labelled.append(man.label(State(flown.data.iloc[start:stop+2])))

        return State.stack(labelled)

    def copy_directions(self, other):
        return Schedule([ms.copy_directions(mo) for ms, mo in zip(self, other)])
