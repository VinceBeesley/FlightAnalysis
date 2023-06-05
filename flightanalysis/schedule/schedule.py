from . import Manoeuvre
from geometry import Transformation, PX
from flightanalysis.state import State
import numpy as np
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
            itrans (Transformation): Transformation to first point of template 
            alinged (State): labelled flight data

        Returns:
            Schedule: new schedule with all the elements resized
        """
        _mans = []
        istate = State.from_transform(Transformation(alinged[0].pos,itrans.att), vel=PX(self[0].elements[0].speed))
        for i, man in enumerate(self):
            man, istate = man.match_intention(
                istate, 
                man.get_data(alinged)
            )
            _mans.append(man)

        return Schedule(_mans)

    def correct_intention(self):
        return self.replace_manoeuvres([man.fix_intention() for man in self])

    def create_matched_template(self, alinged: State) -> State:
        """This will go through all the manoeuvres in a labelled State and create a template with
         only the initial position and speed of each matched"""
        
        iatt = self.create_iatt(alinged[0].direction()[0])

        templates = []
        for manoeuvre in self:
            transform = Transformation(
                manoeuvre.get_data(alinged)[0].pos,
                iatt
            )
            templates.append(manoeuvre.create_template(
                transform, np.mean(abs(alinged.vel))
            ))
            iatt = templates[-1][-1].att

        return State.stack(templates)

    def create_elm_matched_template(self, alinged: State) -> State:
        """This will go through all the elements in a labelled State and create a template 
        with the initial position and speed of each matched"""

        iatt = self.create_iatt(alinged[0].direction()[0])

        templates = []
        for manoeuvre in self:
            mtemps = []
            for elm in manoeuvre.elements:
                transform = Transformation(
                    elm.get_data(alinged)[0].pos,
                    iatt
                )
                mtemps.append(elm.create_template(transform, np.mean(abs(alinged.vel))))
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

            transform = Transformation(
                flown[0].pos,
                iatt
            )
            templates.append(
                man.scale(np.mean(alinged.y) * np.tan(np.radians(60)))
                .create_template(transform, np.mean(abs(alinged.vel)))
            )
            iatt = templates[-1][-1].att
        return templates

    def copy_directions(self, other):
        return Schedule([ms.copy_directions(mo) for ms, mo in zip(self, other)])
