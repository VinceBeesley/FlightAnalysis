from __future__ import annotations
from geometry import Transformation, Quaternion, Coord, P0, PX, PY, PZ
from flightanalysis.state import State
from flightanalysis.schedule.elements import *
from typing import List, Union, Tuple
import numpy as np
import pandas as pd


_els = {c.__name__: c for c in El.__subclasses__()}


class Manoeuvre():
    def __init__(self, entry_line: Line, elements: Union[Elements, list], exit_line: Line, uid: str = None):
        self.entry_line = entry_line
        self.elements = elements if isinstance(elements, Elements) else Elements(elements)
        self.exit_line = exit_line
        self.uid = uid
    
    @staticmethod
    def from_dict(data):
        return Manoeuvre(
            Line.from_dict(data["entry_line"]) if data["entry_line"] else None,
            Elements.from_dicts(data["elements"]),
            Line.from_dict(data["exit_line"]) if data["exit_line"] else None,
            data["uid"]
        )

    def to_dict(self):
        return dict(
            entry_line=self.entry_line.to_dict() if self.entry_line else None,
            elements=self.elements.to_dicts(),
            exit_line=self.exit_line.to_dict() if self.exit_line else None,
            uid=self.uid
        )

    @staticmethod
    def from_all_elements(uid:str, els: List[El]):
        hasentry = 1 if els[0].uid.startswith("entry_") else None
        hasexit = -1 if els[-1].uid.startswith("exit_") else None

        return Manoeuvre(
            els[0] if hasentry else None, 
            els[hasentry:hasexit], 
            els[-1] if hasexit else None, 
            uid
        )

    def all_elements(self, create_entry: bool = False, create_exit: bool = False) -> Elements:
        els = Elements()

        if self.entry_line:
            els.add(self.entry_line)
        elif create_entry:
            els.add(Line(self.elements[0].speed, 30, 0, "entry_line"))

        els.add(self.elements)

        if self.exit_line:
            els.add(self.exit_line)
        elif create_exit:
            els.add(Line(self.elements[0].speed, 30, 0, "exit_line"))

        return els

    def add_lines(self, add_entry=True, add_exit=True):
        return Manoeuvre.from_all_elements(self.uid, self.all_elements(add_entry, add_exit))
    
    def remove_lines(self, remove_entry=True, remove_exit=True):
        return Manoeuvre(
            None if remove_entry else self.entry_line, 
            self.elements, 
            None if remove_exit else self.exit_line, 
            self.uid
        )
    
    def create_template(self, initial: Union[Transformation, State], aligned:State=None) -> State:
        
        istate = State.from_transform(initial, vel=PX()) if isinstance(initial, Transformation) else initial
        aligned = self.get_data(aligned) if aligned else None
        templates = []
        for i, element in enumerate(self.all_elements()):
            time = element.get_data(aligned).time if not aligned is None else None

            if i < len(self.elements)-1 and not time is None:
                time = time.extend()
            templates.append(element.create_template(istate, time))
            istate = templates[-1][-1]
        
        return State.stack(templates).label(manoeuvre=self.uid)


    def get_data(self, st: State):
        return st.get_manoeuvre(self.uid)

    def match_intention(self, istate: State, aligned: State) -> Tuple[Manoeuvre, State]:
        """Create a new manoeuvre with all the elements scaled to match the corresponding 
        flown element"""

        elms = Elements()
        templates = [istate]
        aligned = self.get_data(aligned)

        for i, elm in enumerate(self.all_elements()):
            st = elm.get_data(aligned)
            elms.add(elm.match_intention(
                templates[-1][-1].transform, 
                st
            ))

            if isinstance(elms[-1], Autorotation):
                #copy the autorotation pitch offset back to the preceding pitch departure
                angles = np.arctan2(st.vel.z, st.vel.x)
                pos_break = max(angles)
                neg_break = min(angles)
                elms[-2].break_angle = pos_break if pos_break > -neg_break else neg_break
                
            templates.append(elms[-1].create_template(
                templates[-1][-1], 
                st.time.extend() if i < len(self.elements) - 1 else st.time
            ))
                    
        return Manoeuvre.from_all_elements(self.uid, elms), State.stack(templates[1:]).label(manoeuvre=self.uid)

    def match_rates(self, rates):
        new_elms = [elm.match_axis_rate(rates[elm.__class__], rates["speed"]) for elm in self.elements]
        return self.replace_elms(new_elms)

    def copy_directions(self, other: Manoeuvre):
        return Manoeuvre.from_all_elements(
            self.uid, 
            [es.copy_direction(eo) for es, eo in zip(self.all_elements(), other.all_elements())]
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