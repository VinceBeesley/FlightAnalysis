from geometry import Transformation
from flightanalysis.state import State
from flightanalysis.schedule.elements import Loop, Line, StallTurn, Snap, Spin, get_rates, El, Elements
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

    def __init__(self, name: str, k: float, elements: Elements, uid: str = None):
        # TODO elements needs to change to a custom elements collection with
        #element access by attribute
        self.name = name
        self.k = k
        self.elements = elements  
        
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



    def match_rates(self, rates):
        new_elms = [elm.match_axis_rate(rates[elm.__class__], rates["speed"]) for elm in self.elements]
        return self.replace_elms(new_elms)
