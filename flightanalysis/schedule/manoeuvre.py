from geometry import Transformation, Quaternion, Coord, P0, PX, PY, PZ
from flightanalysis.state import State
from flightanalysis.schedule.elements import Loop, Line, StallTurn, Snap, Spin, get_rates, El, Elements
from flightanalysis.schedule.figure_rules import IMAC, rules, Rules
from typing import List, Union
import numpy as np
import pandas as pd


_els = {c.__name__: c for c in El.__subclasses__()}


class Manoeuvre():
    def __init__(self, entry_line: Line, elements: Union[Elements, list], uid: str = None):
        self.entry_line = entry_line
        self.elements = elements if isinstance(elements, Elements) else Elements(elements)
        self.uid = uid
    
    @staticmethod
    def from_dict(data):
        return Manoeuvre(
            Line.from_dict(data["entry_line"]),
            Elements.from_dicts(data["elements"]),
            data["uid"]
        )

    @staticmethod
    def from_all_elements(uid:str, els: List[El]):
        return Manoeuvre(els[0], els[1:], uid)

    @property
    def all_elements(self):
        return Elements([self.entry_line, *self.elements.to_list()]) if not self.entry_line is None else self.elements

    def create_template(self, transform: Transformation) -> State:
        itrans = transform
        templates = []
        for i, element in enumerate(self.all_elements):
            templates.append(element.create_template(itrans))
            itrans = templates[-1][-1].transform
        
        return State.stack(templates).label(manoeuvre=self.uid)

    def get_data(self, sec: State):
        return State(sec.data.loc[sec.data.manoeuvre == self.uid])

    def match_intention(self, transform: Transformation, flown: State):
        """Create a new manoeuvre with all the elements scaled to match the corresponding 
        flown element"""

        elms = []
        flown = self.get_data(flown)

        for elm in self.all_elements:
            elms.append(elm.match_intention(
                transform, 
                elm.get_data(flown)
            ))
            try:
                transform = elms[-1].create_template(
                    transform
                )[-1].transform
            except Exception as ex:
                print(f"Error creating template for {elm.__class__.__name__}, {elm.__dict__}")
                print(str(ex))
                raise Exception("Error Creating Template")

        return Manoeuvre(elms[0], Elements(elms[1:]), self.uid), transform

    def match_rates(self, rates):
        new_elms = [elm.match_axis_rate(rates[elm.__class__], rates["speed"]) for elm in self.elements]
        return self.replace_elms(new_elms)

    def copy_directions(self, other):
        return Manoeuvre.from_all_elements(
            self.uid, 
            [es.copy_direction(eo) for es, eo in zip(self.all_elements, other.all_elements)]
        )
