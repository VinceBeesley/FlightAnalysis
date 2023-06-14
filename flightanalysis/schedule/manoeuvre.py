from geometry import Transformation, Quaternion, Coord, P0, PX, PY, PZ
from flightanalysis.state import State
from flightanalysis.schedule.elements import *
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

    def to_dict(self):
        return dict(
            entry_line=self.entry_line.to_dict(),
            elements=self.elements.to_dicts(),
            uid=self.uid
        )

    @staticmethod
    def from_all_elements(uid:str, els: List[El]):
        return Manoeuvre(els[0], els[1:], uid)

    def all_elements(self, exit_line=False):
        els = []

        if not self.entry_line is None:
            els.append(self.entry_line)
        else:
            els.append(Line(self.elements[0].speed, 30, 0, "entry_line"))

        for el in self.elements:
            els.append(el)

        if exit_line:
            els.append(Line(els[-1].speed, 30, 0, "exit_line"))
        
        return Elements(els)


    def create_template(self, initial: Union[Transformation, State], flown:State=None) -> State:
        
        istate = State.from_transform(initial, vel=PX()) if isinstance(initial, Transformation) else initial
        
        templates = []
        els = self.all_elements()
        for i, element in enumerate(els):
            time = element.get_data(flown).time if not flown is None else None
            if i < len(els)-1 and not time is None:
                time = time.extend()
            templates.append(element.create_template(istate, time))
            istate = templates[-1][-1]
        
        return State.stack(templates).label(manoeuvre=self.uid)

    def get_data(self, st: State):
        return st.get_manoeuvre(self.uid)

    def match_intention(self, istate: State, flown: State):
        """Create a new manoeuvre with all the elements scaled to match the corresponding 
        flown element"""

        elms = []
        flown = self.get_data(flown)

        for elm in self.all_elements():
            st = elm.get_data(flown)
            elms.append(elm.match_intention(
                istate.transform, 
                st
            ))

            if isinstance(elms[-1], Autorotation):
                #copy the autorotation pitch offset back to the preceding pitch departure
                angles = np.arctan2(st.vel.z, st.vel.x)
                pos_break = max(angles)
                neg_break = min(angles)
                elms[-2].break_angle = pos_break if pos_break > -neg_break else neg_break

            istate = elms[-1].create_template(istate)[-1]
        
        return Manoeuvre(elms[0], Elements(elms[1:]), self.uid), istate

    def match_rates(self, rates):
        new_elms = [elm.match_axis_rate(rates[elm.__class__], rates["speed"]) for elm in self.elements]
        return self.replace_elms(new_elms)

    def copy_directions(self, other):
        return Manoeuvre.from_all_elements(
            self.uid, 
            [es.copy_direction(eo) for es, eo in zip(self.all_elements, other.all_elements)]
        )

    def analyse(self, flown: State, template: State):
        
        fl=self.entry_line.get_data(flown)
        tp=self.entry_line.get_data(template).relocate(fl.pos[0])
        
        ers = [ElResults(self.entry_line, self.entry_line.analyse_exit(fl, tp))]

        for el in self.elements:
            fl = el.get_data(flown)
            tp = el.get_data(template).relocate(fl.pos[0])
            ers.append(ElResults(el, el.analyse(fl, tp)))
        return ElementsResults(ers)

    def descriptions(self):
        return [e.describe() for e in self.elements]