"""This module contains the structures used to describe the elements within a manoeuvre and
their relationship to each other. 

A Manoeuvre contains a dict of elements which are constructed in order. The geometry of these
elements is described by a set of high level parameters, such as loop radius, combined line 
length of lines, roll direction. 

A complete manoeuvre description includes a set of functions to create the elements based on
the higher level parameters and another set of functions to collect the parameters from the 
elements collection.

"""
from __future__ import annotations
import enum
from typing import List, Dict, Callable, Union, Tuple
import numpy as np
from flightanalysis.schedule.elements import Line, Elements
from flightanalysis.schedule.manoeuvre import Manoeuvre
from flightanalysis.schedule.definition.manoeuvre_info import ManInfo
from flightanalysis import State
from geometry import Transformation, Euler, Point, P0
from functools import partial
from . import ManParm, ManParms, ElDef, ElDefs, _a, Position, Direction
from copy import deepcopy


class ManDef:
    """This is a class to define a manoeuvre for template generation and judging.

    It also contains lots of helper functions for creating elements and common combinations
    of elements.
    """

    def __init__(self, info: ManInfo, mps: ManParms = None, eds: ElDefs = None):
        self.info: ManInfo = info
        self.mps: ManParms = ManParms.create_defaults_f3a() if mps is None else mps
        self.eds: ElDefs = ElDefs() if eds is None else eds

    @property
    def uid(self):
        return self.info.short_name

    def to_dict(self):
        return dict(
            info = self.info.to_dict(),
            mps = self.mps.to_dict(),
            eds = self.eds.to_dict()
        )

    @staticmethod
    def from_dict(data: dict) -> ManDef:
        info = ManInfo.from_dict(data["info"])
        mps = ManParms.from_dict(data["mps"])
        eds = ElDefs.from_dict(data["eds"], mps)
        return ManDef(info, mps, eds)


    def create_entry_line(self, itrans: Transformation=None) -> ElDef:
        """Create a line definition connecting Transformation to the start of this manoeuvre.

        The length of the line is set so that the manoeuvre is centred or extended to box
        edge as required.

        Args:
            itrans (Transformation): The location to draw the line from, usually the end of the last manoeuvre.

        Returns:
            ElDef: A Line element that will position this manoeuvre correctly.
        """
        itrans = self.info.initial_transform(170, 1) if itrans is None else itrans
                
        heading = np.sign(itrans.rotation.transform_point(Point(1, 0, 0)).x[0]) # 1 for +ve x heading, -1 for negative x

        #Create a template, at zero
        man = self._create()
        template = man.create_template(
            State.from_transform(Transformation(
                Point(0,0,0),
                Euler(self.info.start.o.roll_angle(), 0, 0)
        )))
          
        if self.info.position == Position.CENTRE:
            if self.info.centre_loc == -1:
                man_start_x = -(max(template.pos.x) + min(template.pos.x))/2  # distance from start to centre
            else:
                man_start_x = -man.elements[self.info.centre_loc].get_data(template).pos.x[0]
        elif self.info.position ==  Position.END:
                box_edge = np.tan(np.radians(60)) * (np.abs(template.pos.y) + itrans.pos.y[0]) #x location of box edge at every point
                #TODO this should be rotated not absoluted 
                man_start_x = min(box_edge - template.pos.x) 
        
        return ElDef.build(
            Line,
            f"entry_line", 
            30.0, 
            max(man_start_x - itrans.translation.x[0] * heading, 30), 
            0)

    def create(self, itrans=None, depth=None, wind=None) -> Manoeuvre:
        """Create the manoeuvre based on the default values in self.mps.

        Returns:
            Manoeuvre: The manoeuvre
        """
        
        return Manoeuvre(
            self.create_entry_line(
                self.info.initial_transform(depth, wind) if itrans is None else itrans
            )(self.mps),
            Elements([ed(self.mps) for ed in self.eds]), 
            None,
            uid=self.info.short_name
        )

    def _create(self) -> Manoeuvre:
        return Manoeuvre(
            None,
            Elements([ed(self.mps) for ed in self.eds]),
            None,
            uid=self.info.name
        )


    def get_f3a_rates(self, rolls: ManParm) -> List[ManParm]:
        rates = []
        for roll in rolls.value:
            if abs(roll) >= 2 * np.pi:
                rates.append(self.mps.continuous_roll_rate)
            else:
                rates.append(self.mps.partial_roll_rate)
        return rates            

