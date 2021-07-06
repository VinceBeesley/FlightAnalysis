
from typing import Dict
from enum import Enum
from uuid import uuid4
import numpy as np
from geometry import Transformation, Point, scalar_projection, Points
from flightanalysis import Section
from uuid import uuid4
from scipy import optimize

class El:
    def __init__(self):
        self.uid = str(uuid4())

    def get_data(self, sec: Section):
        return Section(sec.data.loc[sec.data.element == self.uid])

    def _add_rolls(self, el: Section, rolls: float) -> Section:
        if not rolls == 0:
            el = el.superimpose_roll(rolls)
        el.data["element"] = self.uid
        return el 

class LineEl(El):
    def __init__(self, length, rolls=0):
        super().__init__()
        self.length = length
        self.rolls = rolls

    def create_template(self, transform: Transformation, speed: float, scale: float):
        el = Section.from_line(transform, speed, scale * self.length)
        return self._add_rolls(el, self.rolls)

    def resize(self, sec: Section, transform: Transformation):
        return LineEl(
            scalar_projection(
                sec.get_state_from_index(-1).pos - sec.get_state_from_index(0).pos,
                transform.rotate(Point.X())
            ),
            self.rolls
        )
class LoopEl(El):
    def __init__(self, diameter: float, loops:float, rolls=0.0, ke:bool=False):
        super().__init__()
        self.loops = loops
        self.diameter = diameter
        self.rolls = rolls
        self.ke=ke

    def create_template(self, transform: Transformation, speed: float, scale: float):
        el = Section.from_loop(transform, speed, self.loops, 0.5 * scale * self.diameter, self.ke)
        return self._add_rolls(el, self.rolls)

    def resize(self, sec: Section, transform: Transformation): 
        pos = transform.rotate(Points.from_pandas(sec.pos))

        _x = pos.x
        _y = pos.y if self.ke else pos.z

        def calc_R(xc, yc): return np.sqrt((_x-xc)**2 + (_y-yc)**2)

        def f_2(c):
            Ri = calc_R(*c)
            return Ri - Ri.mean()
        
        center_2, ier = optimize.leastsq(f_2, (_x.mean(), _y.mean()))
        Ri_2 = calc_R(*center_2)

        return LoopEl(2 * Ri_2.mean(),self.loops, self.rolls, self.ke)

class SpinEl(El):
    def __init__(self, length: float, turns:float, opp_turns: float=0.0):
        super().__init__()
        self.length = length
        self.turns = turns
        self.opp_turns = opp_turns
    
    def create_template(self, transform: Transformation, speed: float, scale: float):
        el = Section.from_spin(transform, scale * self.length, self.turns, self.opp_turns)
        return self._add_rolls(el, 0.0)

class SnapEl(El):
    def __init__(self, length: float, rolls: float):
        super().__init__()
        self.length = length
        self.rolls = rolls
    
    def create_template(self, transform: Transformation, speed: float, scale: float):
        el = Section.from_line(transform, speed, scale * self.length)
        return self._add_rolls(el, self.rolls)

class StallTurnEl(El):
    def __init__(self, direction: int=1, duration: float=1.0):
        super().__init__()
        self.direction = direction
        self.duration = duration

    def create_template(self, transform: Transformation, speed: float, scale: float):
        el= Section.from_loop(transform, 3.0, 0.5 * self.direction, 2.0, True)
        return self._add_rolls(el, 0.0)



def rollmaker(num: int, arg: str, denom: float, length: float = 0.5, position="Centre", right=False, rlength=0.3):
    """generate a list of elements representing a roll or point roll
    examples:
    2 points of a 4 point roll: rollmaker(2, "X", 4)
    half a roll: rollmaker(1, "/", 2)
    Args:
        num (int): numerator 
        arg (str): operator, either "X" for point rolls, or "/" for continous rolls
        denom (float): denominator
    """
    lsum = 0.0
    direction = -1 if right else 1
    if arg == "/":
        lsum += rlength * num / denom
        elms = [LineEl(rlength * num / denom, direction * num / denom)]
    elif arg == "X":
        elms = []
        for i in range(num):
            lsum += rlength / denom
            elms.append(LineEl(rlength /denom, direction / denom))
            if i < num - 1:
                elms.append(LineEl(0.05, 0.0))
                lsum += 0.05
    else:
        raise KeyError
    return paddinglines(position, length, lsum, elms)


def reboundrollmaker(rolls: list, length: float = 0.5, position="Centre", rlength=0.3, snap=False):
    lsum = 0.0
    elms = []
    last_dir = -np.sign(rolls[0])
    for roll in rolls:
        if last_dir == np.sign(roll):
            elms.append(LineEl(0.05, 0.0))
            lsum += 0.05
        last_dir = np.sign(roll)
        if snap:
            elms.append(SnapEl(rlength * abs(roll), roll))
        else:
            elms.append(LineEl(rlength * abs(roll), roll))
        lsum += rlength * abs(roll)
    return paddinglines(position, length, lsum, elms)


def rollsnapcombomaker(rolls: list, length: float, position="Centre", rlength=0.3):
    lsum = 0.0
    elms = []
    last_dir = -np.sign(rolls[0][1])
    for roll in rolls:
        # add pause if roll in opposite direction
        if last_dir == np.sign(roll[1]):
            elms.append(LineEl(0.05, 0.0))
            lsum += 0.05
        last_dir = np.sign(roll[1])
        if roll[0] == "snap":
            elms.append(SnapEl(0.05 * abs(roll[1]), roll[1]))
            lsum += 0.05 * abs(roll[1])
        if roll[0] == "roll":
            elms.append(LineEl(rlength *abs(roll[1]), roll[1]))
            lsum += rlength * abs(roll[1])
    return paddinglines(position, length, lsum, elms)


def paddinglines(position, length, lsum, elms):
    lleft = length - lsum
    if position.lower() == "centre":
        return [
            LineEl(lleft / 2, 0.0)
        ] + elms + [
            LineEl(lleft / 2, 0.0)
        ]
    elif position.lower() == "start":
        return elms + [LineEl(lleft, 0.0)]
    elif position.lower() == "end":
        return [LineEl(lleft, 0.0)] + elms
