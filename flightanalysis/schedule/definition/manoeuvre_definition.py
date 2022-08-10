"""This module contains the structures used to describe the elements within a manoeuvre and
their relationship to each other. 

A Manoeuvre contains a dict of elements which are constructed in order. The geometry of these
elements is described by a set of high level parameters, such as loop radius, combined line 
length of lines, roll direction. 

A complete manoeuvre description includes a set of functions to create the elements based on
the higher level parameters and another set of functions to collect the parameters from the 
elements collection.

TODO Tidy all the helper functions
TODO Scale the manoeuvres defaults so they fit in a box
TODO Define a serialisation format


"""
import enum
from typing import List, Dict, Callable, Union, Tuple
import numpy as np
import pandas as pd
from numbers import Number
from flightanalysis.schedule.elements import Loop, Line, Snap, Spin, StallTurn, El, Elements
from flightanalysis.schedule.manoeuvre import Manoeuvre
from flightanalysis.schedule.definition.manoeuvre_info import ManInfo
from flightanalysis.criteria.comparison import Comparison, f3a_speed, f3a_radius, f3a_length, f3a_roll_rate, f3a_free
from flightanalysis.criteria.local import Combination
from geometry import Transformation, Euler, Point, P0
from functools import partial
from scipy.optimize import minimize
from . import ManParm, ManParms, ElDef, ElDefs, _a, MPValue, Position, Direction
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
        wind = self.info.start.d.get_wind(heading) # is wind in +ve or negative x direction?

        #Create a template, at zero
        template = self._create().create_template(Transformation(
            Point(0,0,0),
            Euler(self.info.start.o.roll_angle(), 0, 0)
        ))
          
        
        match self.info.position:
            case Position.CENTRE:
                man_start_x = -(max(template.pos.x) + min(template.pos.x))/2  # distance from start to centre
            case Position.END:
                box_edge = np.tan(np.radians(60)) * (np.abs(template.pos.y) + itrans.pos.y[0]) #x location of box edge at every point
                #TODO this should be rotated not absoluted 
                man_start_x = min(box_edge - template.pos.x) 
        
        return ElDef.line(
            f"entry_{self.info.short_name}", 
            self.mps.speed, 
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
            uid=self.info.short_name
        )

    def _create(self) -> Manoeuvre:
        return Manoeuvre(
            None,
            Elements([ed(self.mps) for ed in self.eds]), 
            uid=self.info.name
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

    def add_stallturn(self, s=None, rate=None) -> ElDef:
        self.eds.add(ElDef.stallturn(
            self.eds.get_new_name(),
            self.mps.speed if s is None else s,
            self.mps.stallturn_rate if rate is None else rate
        ))


    def add_snap(
        self,
        roll: Union[float, ManParm, Callable],
        direction: Union[int, ManParm, Callable],
        rate: Union[float, ManParm, Callable]=None,
        s: Union[ManParm, Callable]=None
    ) -> ElDef:
        return self.eds.add(ElDef.snap(
            self.eds.get_new_name(),
            self.mps.speed if s is None else s, 
            self.mps.snap_rate if rate is None else rate,
            roll,
            direction
        ))

    def add_spin(
        self,
        turns: List[List[float]],
        rate: Union[float, ManParm, Callable]=None
    ):
        turns = self.mps.add(ManParm(
            self.mps.next_free_name("spins_"),
            Combination(turns),
            0
        ))
        return self.eds.add(ElDef.spin(
            self.eds.get_new_name(),
            20,
            turns.valuefunc(0),
            turns.valuefunc(1) if turns.n == 2 else 0,
            self.mps.spin_rate if rate is None else rate
        ))

    def add_padded_snap(
        self,
        roll:List[List[float]],
        direction:int=None,
        s=None,
        rate=None,
        l=None,
        criteria=f3a_length
    ):
        return self.add_and_pad_els(
            ElDefs([ElDef.snap(
                self.eds.get_new_name(),
                self.mps.speed if s is None else s, 
                self.mps.snap_rate if rate is None else rate,
                self.mps.add(ManParm(
                    self.mps.next_free_name("snaproll_"),
                    Combination(roll), 
                    0
                )),
                self.mps.add(ManParm(
                    self.mps.next_free_name("snapdirection_"),
                    Combination([[1], [-1]] if direction is None else [[direction]]),
                    0
                )) 
            )]), l, s, criteria
        )

    def add_simple_snap(
        self,
        roll:List[float],
        direction:int=None,
        s=None,
        rate=None
    ):
        return self.add_snap(
            self.mps.add(ManParm(
                self.mps.next_free_name("snaproll_"),
                Combination([roll]),
                0
            )),
            self.mps.add(ManParm(
                self.mps.next_free_name("snapdirection_"),
                Combination([[1, -1 ]] if direction is None else [[direction]]),
                0
            )),
            rate,
            s
        )

    def add_simple_roll(self, rolls:str, s=None, l=None, rates=None, pause=None, criteria=f3a_length):
        self.add_padded_roll_combo(
            self.mps.add(
                ManParm(
                    self.mps.next_free_name("roll_"), 
                    Combination.rollcombo(rolls), 
                    0
                )
            ), 
            rates=rates, s=s, l=l, pause=pause, criteria=criteria
        )

    def get_f3a_rates(self, rolls: ManParm) -> List[ManParm]:
        rates = []
        for roll in rolls.value:
            if abs(roll) >= 2 * np.pi:
                rates.append(self.mps.continuous_roll_rate)
            else:
                rates.append(self.mps.partial_roll_rate)
        return rates            



    def add_padded_roll_combo(
        self, 
        rolls: ManParm, 
        rates: List[ManParm] = None,
        s: Union[ManParm, Callable]=None,
        l: Union[ManParm, Callable] = None,
        pause: Union[ManParm, Callable] = None,
        criteria=f3a_length
    ):

        roll_els = ElDefs.create_roll_combo(
            f"{self.eds.get_new_name()}_1",  # TODO fiddling with the names like this is a bodge
            rolls, 
            self.mps.speed if s is None else s,
            self.get_f3a_rates(rolls) if rates is None else rates,
            self.mps.point_length if pause is None else pause
        )

        return self.add_and_pad_els(roll_els, l, s, criteria)

    def add_roll_combo(
        self,rolls:Union[ManParm, List[float]], 
        reversible: bool = True,
        rates: List[ManParm] = None,
        s=None,
        pause=None
    ):
        
        if not isinstance(rolls,ManParm):
            rolls = self.mps.add(ManParm("roll_combo", Combination.rolllist(rolls, reversible), 0))

        return self.eds.add(ElDefs.create_roll_combo(
            self.eds.get_new_name(),
            rolls,
            self.mps.speed if s is None else s,
            self.get_f3a_rates(rolls) if rates is None else rates,
            self.mps.point_length if pause is None else pause
        ))



    def add_and_pad_els(self, eds: ElDefs, l=None, s=None, criteria=f3a_length):
        """Add an elements collection to this manoeuvre and pad it so that it sits between two
        lines of equal length so that the total length is equal to l. 
        also creates a ManParm to collect and score the two padding lines lengths.

        Args:
            eds (ElDefs): _description_
            l (Union[ManParm, Callable], optional): the total length. Defaults to None and so picks up mps.line_length.
            s (Union[ManParm, Callable], optional): the speed. Defaults to None and so picks up mps.speed.
            criteria (Comparison, optional): Comparison criteria to use for the padding lines. Defaults to f3a_length.

        Returns:
            List[ElDef]: All the elements in order. These will also have been added to self.edefs.
        """
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

    def default_finder(
        self, 
        wind=1, 
        depth=170, 
        variables: Dict[str,MPValue]=None
    ):
        
        nmd = deepcopy(self)

        if not variables:
            variables = dict(
                loop_radius=MPValue(55, 30, 70, 1),
                line_length=MPValue(130, 30, 200, 1)
            )

        itrans = nmd.info.initial_transform(depth, wind)
        end_h = nmd.info.end.h.calculate(depth)

        def cost_fn(vars):
            for k, v in zip(variables.keys(), vars):
                nmd.mps.parms[k].default = v
            template = nmd.create().create_template(itrans)
            h_cost = 10 * abs(template[-1].pos.z[0] - end_h)**2
            v_cost = [v.slope * abs((v.value - nv)) for v, nv in zip(variables.values(), vars)]

            costs = v_cost + [h_cost]
            print(costs)
            return sum(costs)

        res = minimize(cost_fn, [v.value for v in variables.values()], tol=1.0)
        return nmd