
from typing import Dict
from enum import Enum
from uuid import uuid4
import numpy as np
from geometry import Transformation
from flightanalysis import Section
from uuid import uuid4


class ElClass(Enum):
    LINE = 0
    LOOP = 1
    KELOOP = 2
    SPIN = 4
    STALLTURN = 5
    SNAP = 6


class Element():
    def __init__(
        self,
        classification: ElClass,
        size: float,
        roll: float,
        loop: float
    ):
        self.classification = classification
        self.size = size
        self.roll = roll
        self.loop = loop
        self.uid = str(uuid4())

    def create_template(self, transform: Transformation, speed: float, scale: float) -> Section:
        """This creates a Section, with an additional element column tagged with the instances uid

        Args:
            transform (Transformation): initial position and orientation
            speed (float): [description]
            scale (float): [description]

        Returns:
            [type]: [description]
        """
        if self.classification == ElClass.LOOP:
            el = Section.from_loop(
                transform, speed, self.loop, 0.5 * scale * self.size, False)
        elif self.classification == ElClass.KELOOP:
            el = Section.from_loop(
                transform, speed, self.loop, 0.5 * scale * self.size, True)
        elif self.classification == ElClass.LINE:
            el = Section.from_line(transform, speed, scale * self.size)
        elif self.classification == ElClass.SPIN:
            return Section.from_spin(transform, scale * self.size, self.roll, self.loop)
        elif self.classification == ElClass.SNAP:
            el = Section.from_line(transform, speed, scale * self.size)
        elif self.classification == ElClass.STALLTURN:
            _dir = 1 if self.loop >= 0.0 else -1
            return Section.from_loop(transform, 3.0, 0.5 * _dir, 2.0, True)

        if not self.roll == 0:
            el = el.superimpose_roll(self.roll)

        el.data["element"] = self.uid

        return el

    def get_data(self, sec: Section):
        return Section(sec.data.loc[sec.data.element == self.uid])


class El:
    def __init__(self):
        self.uid = str(uuid4())

    def get_data(self, sec: Section):
        return Section(sec.data.loc[sec.data.element == self.uid])

    def _add_rolls(self, sec: Section, rolls: float) -> Section:
        if not rolls == 0:
            el = sec.superimpose_roll(rolls)
        el.data["element"] = self.uid
        return el 

class LineEl(El):
    def __init__(self, length, rolls=0):
        super().__init__()
        self.length = length
        self.rolls = rolls

    def create_template(self, transform: Transformation, speed: float, scale: float):
        el = Section.from_line(transform, speed, scale * self.length)
        return self._add_rolls(self, el, self.rolls)

class LoopEl(El):
    def __init__(self, radius, ke:bool=False, rolls=0):
        super().__init__()
        self.radius = radius
        self.rolls = rolls
        self.ke=ke

    def create_template(self, transform: Transformation, speed: float, scale: float):
        el = Section.from_loop(transform, speed, self.loop, 0.5 * scale * self.size, self.ke)
        return self._add_rolls(self, el, self.rolls)

class SpinEl(El):
    def __init__(self, size: float, turns:float, opp_turns: float=0.0):
        super().__init__()
        self.size = size
        self.turns = turns
        self.opp_turns = opp_turns
    
    def create_template(self, transform: Transformation, speed: float, scale: float):
        el = Section.from_spin(transform, scale * self.size, self.turns, self.opp_turns)
        return self._add_rolls(self, el, 0.0)

class SnapEl(El):
    def __init__(self, length: float, rolls: float):
        super().__init__()
        self.length = length
        self.rolls = rolls
    
    def create_template(self, transform: Transformation, speed: float, scale: float):
        el = Section.from_line(transform, speed, scale * self.length)
        return self._add_rolls(self, el, self.rolls)

class StallTurnEl(El):
    def __init__(self, direction: int, rate: float):
        super().__init__()
        self.direction = direction
        self.rate = rate

    def create_template(self, transform: Transformation, speed: float, scale: float):
        el= Section.from_loop(transform, 3.0, 0.5 * self.direction, 2.0, True)
        return self._add_rolls(self, el, 0.0)



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
        elms = [Element(ElClass.LINE, rlength * num / denom,
                        direction * num / denom, 0.0)]
    elif arg == "X":
        elms = []
        for i in range(num):
            lsum += rlength / denom
            elms.append(Element(ElClass.LINE, rlength /
                                denom, direction / denom, 0.0))
            if i < num - 1:
                elms.append(Element(ElClass.LINE, 0.05, 0.0, 0.0))
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
            elms.append(Element(ElClass.LINE, 0.05, 0.0, 0.0))
            lsum += 0.05
        last_dir = np.sign(roll)
        elms.append(Element(ElClass.SNAP if snap else ElClass.LINE,
                            rlength * abs(roll), roll, 0.0))
        lsum += rlength * abs(roll)
    return paddinglines(position, length, lsum, elms)


def rollsnapcombomaker(rolls: list, length: float, position="Centre", rlength=0.3):
    lsum = 0.0
    elms = []
    last_dir = -np.sign(rolls[0][1])
    for roll in rolls:
        # add pause if roll in opposite direction
        if last_dir == np.sign(roll[1]):
            elms.append(Element(ElClass.LINE, 0.05, 0.0, 0.0))
            lsum += 0.05
        last_dir = np.sign(roll[1])
        if roll[0] == "snap":
            elms.append(Element(ElClass.SNAP, 0.05 *
                                abs(roll[1]), roll[1], 0.0))
            lsum += 0.05 * abs(roll[1])
        if roll[0] == "roll":
            elms.append(Element(ElClass.LINE, rlength *
                                abs(roll[1]), roll[1], 0.0))
            lsum += rlength * abs(roll[1])
    return paddinglines(position, length, lsum, elms)


def paddinglines(position, length, lsum, elms):
    lleft = length - lsum
    if position.lower() == "centre":
        return [
            Element(ElClass.LINE, lleft / 2, 0.0, 0.0)
        ] + elms + [
            Element(ElClass.LINE, lleft / 2, 0.0, 0.0)
        ]
    elif position.lower() == "start":
        return elms + [Element(ElClass.LINE, lleft, 0.0, 0.0)]
    elif position.lower() == "end":
        return [Element(ElClass.LINE, lleft, 0.0, 0.0)] + elms
