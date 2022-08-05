"""This module contains the structures used to describe the elements within a manoeuvre and
their relationship to each other. 

A Manoeuvre contains a dict of elements which are constructed in order. The geometry of these
elements is described by a set of high level parameters, such as loop radius, combined line 
length of lines, roll direction. 

A complete manoeuvre description includes a set of functions to create the elements based on
the higher level parameters and another set of functions to collect the parameters from the 
elements collection.
"""
import enum
from typing import List, Dict, Callable, Union
import numpy as np
import pandas as pd
from numbers import Number
from flightanalysis.schedule.elements import Loop, Line, Snap, Spin, StallTurn, El, Elements
from flightanalysis.schedule.manoeuvre import Manoeuvre
from flightanalysis.criteria.comparison import Comparison, f3a_speed, f3a_radius, f3a_length, f3a_roll_rate
from flightanalysis.criteria.local import Combination

from functools import partial

from . import ManParm, ManParms, ElDef, ElDefs, _a






class ManDef:
    """This is a class to define a manoeuvre for template generation and judging.

    It also contains lots of helper functions for creating elements and common combinations
    of elements.
    """

    def __init__(self, name, mps: ManParms = None, eds: ElDefs = None):
        self.name: str = name
        self.mps: ManParms = ManParms() if mps is None else mps
        self.eds: ElDefs = ElDefs() if eds is None else eds

    def create(self):
        return Manoeuvre(self.name, 2, Elements.from_list([ed(self.mps) for ed in self.eds]))

    @staticmethod
    def basic_f3a(name):
        return ManDef(
            name,
            ManParms.from_list([
                ManParm("speed", f3a_speed, 30.0),
                ManParm("loop_radius", f3a_radius, 55.0),
                ManParm("line_length", f3a_length, 130.0),
                ManParm("point_length", f3a_length, 10.0),
                ManParm("continuous_roll_rate", f3a_roll_rate, np.pi),
                ManParm("partial_roll_rate", f3a_roll_rate, np.pi)
            ])
        )

    def add_loop(
        self,
        angle: Union[float, ManParm, Callable],
        roll: Union[float, ManParm, Callable]=0.0,
        ke: bool=False,
        s: Union[ManParm, Callable]=None,
        r: Union[ManParm, Callable]=None
    ) -> ElDef:
        
        self.eds.add(ElDef.loop(
            self.eds.get_new_name(), 
            ke,
            self.mps.speed if s is None else s, 
            self.mps.loop_radius if r is None else r, 
            angle, 
            roll
        ))

    def add_line(
        self,
        roll: Union[float, ManParm, Callable]=0.0,
        s: Union[ManParm, Callable]=None,
        l: Union[ManParm, Callable]=None
    ) -> ElDef:
        
        self.eds.add(ElDef.line(
            self.eds.get_new_name(), 
            self.mps.speed if s is None else s, 
            self.mps.line_length if l is None else l, 
            roll
        ))

    def add_roll_combo(
        self, 
        rolls: ManParm, 
        rates: List[ManParm] = None,
        s: Union[ManParm, Callable]=None,
        l: Union[ManParm, Callable] = None,
        pause: Union[ManParm, Callable] = None,
        criteria=f3a_length
    ):
        #get rates if rate is None
        if rates is None:
            rates = []
            for roll in rolls.value:
                if abs(roll) >= 2 * np.pi:
                    rates.append(self.mps.continuous_roll_rate)
                else:
                    rates.append(self.mps.partial_roll_rate)

        roll_els = ElDefs.create_roll_combo(
            f"{self.eds.get_new_name()}_1",  # TODO fiddiling with the names like this is not nice
            rolls, 
            self.mps.speed if s is None else s,
            rates,
            self.mps.point_length if pause is None else pause
        )

        return self.add_and_pad_els(roll_els, l, s, criteria)


    def add_and_pad_els(self, eds: ElDefs, l=None, s=None, criteria=f3a_length):
        name = self.eds.get_new_name()
        l = self.mps.line_length if l is None else l
        s = self.mps.speed if s is None else s
        
        pad_length = lambda mps: 0.5 * (_a(l)(mps) - eds.builder_sum("length")(mps))
        
        e1 = self.eds.add(ElDef.line(f"e_{eds[0].id}_0", s, pad_length, 0))
        e2 = self.eds.add([ed for ed in eds])
        e3 = self.eds.add(ElDef.line(f"e_{eds[0].id}_2", s, pad_length, 0))

        self.mps.add(ManParm(f"{name}_pad_length", criteria, None, [
                     e1.collectors["length"], e3.collectors["length"]]))
        
        if isinstance(l, ManParm):
            l.append(lambda els: sum([e.collectors["length"](els) for e in [e1] + e2 + [e3]]))
        
        return [e1] + e2 + [e3]

    
