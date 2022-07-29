from geometry import Transformation
from flightanalysis.state import State
from flightanalysis.schedule.elements import Loop, Line, StallTurn, Snap, Spin, get_rates, El
from flightanalysis.schedule.figure_rules import IMAC, rules, Rules

import numpy as np
import pandas as pd


_els = {c.__name__: c for c in El.__subclasses__()}


class Manoeuvre():
    _counter = 0
    register = set()

    @staticmethod
    def reset_counter():
        Manoeuvre._counter = 0
        El.reset_counter()

    def __init__(self, name: str, k: float, elements: list, uid: str = None):
        # TODO elements needs to change to a custom elements collection with
        #element access by attribute
        self.name = name
        self.k = k

        if all(isinstance(x, El) for x in elements):
            self.elements = elements  
        elif all(isinstance(x, dict) for x in elements):
            self.elements = [_els[x.pop("type")](**x) for x in elements]
        else:
            self.elements = []
       
        self.uid = Manoeuvre.make_id() if uid is None else uid

        if self.uid in Manoeuvre.register:
            raise Exception("attempting to create a new Manoeuvre with an existing key")
        Manoeuvre.register.add(self.uid)

    @staticmethod
    def make_id():
        i=1
        while f"auto_{i}" in El.register:
            i+=1
        else:
            return f"auto_{i}"

    def to_dict(self):
        data = self.__dict__.copy()
        data["elements"] = [elm.to_dict() for elm in self.elements]
        return data
    
    def scale(self, factor: float):
        return self.replace_elms([elm.scale(factor) for elm in self.elements])

    def create_template(self, transform: Transformation) -> State:
        itrans = transform
        templates = []
        for i, element in enumerate(self.elements):
            templates.append(element.create_template(itrans))
            itrans = templates[-1][-1].transform
        
        return State.stack(templates).label(manoeuvre=self.uid)

    def get_data(self, sec: State):
        return State(sec.data.loc[sec.data.manoeuvre == self.uid])

    def match_intention(self, transform: Transformation, flown: State, speed: float=None):
        """Create a new manoeuvre with all the elements scaled to match the corresponding flown element"""
        elms = []

        for elm in self.elements:
            edata=elm.get_data(flown)
            elms.append(elm.match_intention(transform, edata))
            try:
                transform = elms[-1].create_template(
                    transform, 
                    edata.data.u.mean()
                )[-1].transform
            except Exception as ex:
                print(f"Error creating template for {elm.__class__.__name__}, {elm.__dict__}")
                print(str(ex))
                raise Exception("Error Creating Template")

        return self.replace_elms(elms), transform


    def get_elm_by_type(self, Elm):
        if not isinstance(Elm, list):
            Elm = [Elm]
        return [el for el in self.elements if el.__class__ in Elm]

    @staticmethod
    def filter_elms_by_attribute(elms, **kwargs):
        for key, value in kwargs.items():
            elms = [el for el in elms if getattr(el, key, None) == value]
        return elms

    def get_id_for_element(self, elms):
        if not isinstance(elms, list):
            elms = [elms]
        uids = [elm.uid for elm in elms]
        return [i for i, elm in enumerate(self.elements) if elm.uid in uids]

    def get_elms_by_id(self, elms):
        if not isinstance(elms, list):
            elms = [elms]
        return [elm for i, elm in enumerate(self.elements) if i in elms]

    @staticmethod
    def create_elm_df(elm_list):
        return pd.DataFrame([elm.to_dict() for elm in elm_list])

    def share_seperator(self, next_man): 
        """Take the following manoeuvre and share the entry line (first element)"""
        if self.elements[-1] != next_man.elements[0]:
            return self.append_element(next_man.elements[0].set_parms())
        else:
            return self.replace_elms([])

    def unshare_seperator(self, next_man): 
        """remove the final element if it matches the first element of the next one"""
        if self.elements[-1] == next_man.elements[0]:
            return self.remove_element(self.elements[-1])
        else:
            return self.replace_elms([])


    def match_rates(self, rates):
        new_elms = [elm.match_axis_rate(rates[elm.__class__], rates["speed"]) for elm in self.elements]
        return self.replace_elms(new_elms)

    
    def get_subset(self, sec: State, first_element: int, last_element: int):
        subsec = self.get_data(sec)
        fmanid = self.elements[first_element].uid
        if last_element == -1:
            lmanid = self.elements[-1].uid + 1
        else:
            lmanid = self.elements[last_element].uid

        return State(subsec.data.loc[(subsec.data.element >= fmanid) & (subsec.data.element < lmanid)])

