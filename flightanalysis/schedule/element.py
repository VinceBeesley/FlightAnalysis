
from typing import Dict
from enum import Enum
from uuid import uuid4
import numpy as np
from geometry import Transformation, Point, scalar_projection, Points, scalar_projection
from flightanalysis import Section
from uuid import uuid4
from scipy import optimize


class El:
    _counter = 0
    def __init__(self, uid: int = None):
        if not uid:
            El._counter += 1
            self.uid = El._counter #str(uuid4())
        else:
            self.uid = uid

    def get_data(self, sec: Section):
        return Section(sec.data.loc[sec.data.element == self.uid])

    def _add_rolls(self, el: Section, rolls: float) -> Section:
        if not rolls == 0:
            el = el.superimpose_roll(rolls)
        el.data["element"] = self.uid
        return el

    def __eq__(self, other):
        return self.uid == other.uid


class LineEl(El):
    def __init__(self, length, rolls=0, l_tag=True, uid: str = None):
        super().__init__(uid)
        self.length = length
        self.rolls = rolls
        self.l_tag = l_tag

    def set_parameter(self, length=None, rolls=None, l_tag=None):
        return LineEl(
            length if length is not None else self.length,
            rolls if rolls is not None else self.rolls,
            l_tag if l_tag is not None else self.l_tag,
            self.uid
        )

    def scale(self, factor):
        return self.set_parameter(length=self.length * factor)

    def create_template(self, transform: Transformation, speed: float, simple: bool = False):
        el = Section.from_line(
            transform, speed, self.length, freq=1.0 if simple else None)
        return self._add_rolls(el, self.rolls)

    def match_axis_rate(self, roll_rate: float, speed: float):
        # roll rate in radians per second, speed in m / s
        if not self.rolls == 0.0:
            return self.set_parameter(
                length=2 * np.pi * abs(self.rolls) * speed / roll_rate)
        else:
            return self.set_parameter()

    def match_intention(self, transform: Transformation, flown: Section):
        length = abs(scalar_projection(
            flown.get_state_from_index(-1).pos -
            flown.get_state_from_index(0).pos,
            transform.rotate(Point(1, 0, 0))
        ))
        return self.set_parameter(
            length=length,
            rolls=np.sign(np.mean(Points.from_pandas(flown.brvel).x)) *
            abs(self.rolls)
        )

    def to_dict(self):
        return {
            "type": "LineEl",
            "length": self.length,
            "rolls": self.rolls,
            "l_tag": self.l_tag,
            "uid": self.uid
        }

class LoopEl(El):
    def __init__(self, diameter: float, loops: float, rolls=0.0, ke: bool = False, r_tag=True, uid: str = None):
        super().__init__(uid)
        assert not diameter == 0 and not loops == 0

        self.loops = loops
        self.diameter = diameter
        self.rolls = rolls
        self.ke = ke
        self.r_tag = r_tag

    def scale(self, factor):
        return self.set_parameter(diameter=self.diameter * factor)

    def create_template(self, transform: Transformation, speed: float, simple=False):
        el = Section.from_loop(transform, speed, self.loops,
                               0.5 * self.diameter, self.ke, freq=1.0 if simple else None)
        return self._add_rolls(el, self.rolls)

    def match_axis_rate(self, pitch_rate: float, speed: float):
        return self.set_parameter(diameter=2 * speed / pitch_rate)

    def match_intention(self, transform: Transformation, flown: Section):
        # https://scipy-cookbook.readthedocs.io/items/Least_Squares_Circle.html
        pos = transform.point(Points.from_pandas(flown.pos))

        if self.ke:
            x, y = pos.x, pos.y
        else:
            x, y = pos.x, pos.z

        # TODO this does not constrain the starting point
        def calc_R(xc, yc): return np.sqrt((x-xc)**2 + (y-yc)**2)

        def f_2(c):
            Ri = calc_R(*c)
            return Ri - Ri.mean()

        center, ier = optimize.leastsq(f_2, (np.mean(x), np.mean(y)))

        return self.set_parameter(
            diameter=2 * calc_R(*center).mean(),
            rolls=np.sign(np.mean(Points.from_pandas(flown.brvel).x)) * abs(self.rolls)
        )
        
    def set_parameter(self, diameter=None, loops=None, rolls=None, ke=None, r_tag=None):
        return LoopEl(
            diameter if not diameter is None else self.diameter,
            loops if not loops is None else self.loops,
            rolls if not rolls is None else self.rolls,
            ke if not ke is None else self.ke,
            r_tag if not r_tag is None else self.r_tag,
            self.uid
        )

    def to_dict(self):
        return {
            "type": "LoopEl",
            "loops": self.loops,
            "diameter": self.diameter,
            "rolls": self.rolls,
            "ke": self.ke,
            "r_tag": self.r_tag,
            "uid": self.uid
        }

class SpinEl(El):
    _speed_factor = 1 / 10

    def __init__(self, length: float, turns: float, opp_turns: float = 0.0, uid: str = None):
        super().__init__(uid)
        self.length = length
        self.turns = turns
        self.opp_turns = opp_turns

    def set_parameter(self, length: float = None, turns: float = None, opp_turns: float = None):
        return SpinEl(
            length if length is not None else self.length,
            turns if turns is not None else self.turns,
            opp_turns if opp_turns is not None else self.opp_turns,
            self.uid
        )

    def scale(self, factor):
        return self.set_parameter(length=self.length * factor)

    def create_template(self, transform: Transformation, speed: float, simple: bool = False):
        _inverted = np.sign(transform.rotate(Point(0, 0, 1)).z)

        nose_drop = Section.from_loop(
            transform, 5.0, -0.25 * _inverted, 2.0, False, freq=1.0 if simple else None)
        nose_drop.data["sub_element"] = "nose_drop"

        rotation = Section.from_line(
            nose_drop.get_state_from_index(-1).transform,
            speed * self._speed_factor,
            self.length * self.turns / (self.turns + self.opp_turns),
            freq=1000 if simple else None
        ).superimpose_roll(self.turns)
        rotation.data["sub_element"] = "rotation"

        if self.opp_turns == 0.0:
            sec = Section.stack([nose_drop, rotation])
        else:
            rotation2 = Section.from_line(
                rotation.get_state_from_index(-1).transform,
                speed * self._speed_factor,
                self.length * self.opp_turns / (self.turns + self.opp_turns),
                freq=1000 if simple else None
            ).superimpose_roll(self.opp_turns)

            rotation2.data["sub_element"] = "opp_rotation"

            sec = Section.stack([nose_drop, rotation, rotation2])
        return self._add_rolls(sec, 0.0)

    def match_axis_rate(self, spin_rate, speed: float):
        #LineEl(2 * np.pi * self.rolls * speed / roll_rate, self.rolls)
        return self.set_parameter(
            length=2 * np.pi * (abs(self.turns) + abs(self.opp_turns)) * speed *
            SpinEl._speed_factor / spin_rate
        )

    def match_intention(self, transform: Transformation, flown: Section):
        # TODO doesnt cover opposite turns
        length = abs(flown.get_state_from_index(-1).pos.z -
                     flown.get_state_from_index(0).pos.z)

        return self.set_parameter(
            length=length,
            turns=np.sign(np.mean(Points.from_pandas(flown.brvel).x)) * abs(self.turns),
            opp_turns = 0.0
        )
    
    def to_dict(self):
        return {
            "type": "SpinEl",
            "length": self.length,
            "turns": self.turns,
            "opp_turns": self.opp_turns,
            "uid": self.uid
        }

class SnapEl(El):
    def __init__(self, length: float, rolls: float, l_tag=True, uid: str = None):
        super().__init__(uid)
        self.length = length
        self.rolls = rolls
        self.l_tag = l_tag

    def set_parameter(self, length=None, rolls=None, l_tag=None):
        return SnapEl(
            length if length is not None else self.length,
            rolls if rolls is not None else self.rolls,
            l_tag if l_tag is not None else self.l_tag,
            self.uid
        )

    def scale(self, factor):
        return self.set_parameter(length=self.length * factor)

    def create_template(self, transform: Transformation, speed: float, simple: bool = False):
        el = Section.from_line(
            transform, speed, self.length, freq=1.0 if simple else None)
        return self._add_rolls(el, self.rolls)

    def match_axis_rate(self, snap_rate: float, speed: float):
        return self.set_parameter(length=2 * np.pi * abs(self.rolls) * speed / snap_rate)

    def match_intention(self, transform: Transformation, flown: Section):
        length = abs(scalar_projection(
            flown.get_state_from_index(-1).pos -
            flown.get_state_from_index(0).pos,
            transform.rotate(Point(1, 0, 0))
        ))
        return self.set_parameter(
            length=length,
            rolls=np.sign(
                np.mean(Points.from_pandas(flown.brvel).x)) * abs(self.rolls)
        )

    def to_dict(self):
        return {
            "type": "SnapEl",
            "length": self.length,
            "rolls": self.rolls,
            "l_tag": self.l_tag,
            "uid": self.uid
        }

class StallTurnEl(El):
    _speed_scale = 1 / 20

    def __init__(self, direction: int = 1, width: float = 1.0, uid: str = None):
        super().__init__(uid)
        self.direction = direction
        self.width = width

    def set_parameter(self, direction=None, width=None):
        return StallTurnEl(
            direction if direction is not None else self.direction,
            width if width is not None else self.width,
            self.uid
        )

    def scale(self, factor):
        return self.set_parameter()

    def create_template(self, transform: Transformation, speed: float, simple: bool = False):
        el = Section.from_loop(
            transform,
            StallTurnEl._speed_scale * speed,
            0.5 * self.direction,
            self.width / 2,
            True,
            freq=1.0 if simple else None)
        return self._add_rolls(el, 0.0)

    def match_axis_rate(self, yaw_rate: float, speed: float):
        return self.set_parameter(width=2 * StallTurnEl._speed_scale * speed / yaw_rate)

    def match_intention(self, transform: Transformation, flown: Section):
        return self.set_parameter(
            direction=np.sign(np.mean(Points.from_pandas(flown.brvel).z)),
            width=0.5
        )

    def to_dict(self):
        return {
            "type": "StallTurnEl",
            "direction": self.direction,
            "width": self.width,
            "uid": self.uid
        }


def get_rates(flown: Section):
    brvels = Points.from_pandas(flown.brvel)
    vels = Points.from_pandas(flown.bvel)
    pos = Points.from_pandas(flown.pos)
    return {
        LoopEl: np.percentile(abs(brvels.y), 90),
        LineEl: np.percentile(abs(brvels.x), 95),
        SnapEl: max(abs(brvels.x)),
        StallTurnEl: np.percentile(abs(brvels.z), 99.9),
        SpinEl: np.percentile(abs(brvels.x), 99.5),
        "speed": vels.x.mean(),
        "distance": pos.y.mean(),
    }


def rollmaker(num: int, arg: str, denom: float, length: float = 0.5, position="Centre", right=False, rlength=0.3, l_tag=True):
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
        elms = [LineEl(rlength * num / denom, direction * num / denom, l_tag)]
    elif arg == "X":
        elms = []
        for i in range(num):
            lsum += rlength / denom
            elms.append(LineEl(rlength / denom, direction / denom, l_tag))
            if i < num - 1:
                elms.append(LineEl(0.05, 0.0))
                lsum += 0.05
    else:
        raise KeyError
    return paddinglines(position, length, lsum, elms, l_tag)


def reboundrollmaker(rolls: list, length: float = 0.5, position="Centre", rlength=0.3, snap=False, l_tag=True):
    lsum = 0.0
    elms = []
    last_dir = -np.sign(rolls[0])
    for roll in rolls:
        if last_dir == np.sign(roll):
            elms.append(LineEl(0.05, 0.0, l_tag))
            lsum += 0.05
        last_dir = np.sign(roll)
        if snap:
            elms.append(SnapEl(rlength * abs(roll), roll, l_tag))
        else:
            elms.append(LineEl(rlength * abs(roll), roll, l_tag))
        lsum += rlength * abs(roll)
    return paddinglines(position, length, lsum, elms, l_tag)


def rollsnapcombomaker(rolls: list, length: float, position="Centre", rlength=0.3, l_tag=True):
    lsum = 0.0
    elms = []
    last_dir = -np.sign(rolls[0][1])
    for roll in rolls:
        # add pause if roll in opposite direction
        if last_dir == np.sign(roll[1]):
            elms.append(LineEl(0.05, 0.0, l_tag))
            lsum += 0.05
        last_dir = np.sign(roll[1])
        if roll[0] == "snap":
            elms.append(SnapEl(0.05 * abs(roll[1]), roll[1], l_tag))
            lsum += 0.05 * abs(roll[1])
        if roll[0] == "roll":
            elms.append(LineEl(rlength * abs(roll[1]), roll[1], l_tag))
            lsum += rlength * abs(roll[1])
    return paddinglines(position, length, lsum, elms, l_tag)


def paddinglines(position, length, lsum, elms, l_tag=True):
    lleft = length - lsum
    if position.lower() == "centre":
        return [
            LineEl(lleft / 2, 0.0, l_tag)
        ] + elms + [
            LineEl(lleft / 2, 0.0, l_tag)
        ]
    elif position.lower() == "start":
        return elms + [LineEl(lleft, 0.0)]
    elif position.lower() == "end":
        return [LineEl(lleft, 0.0)] + elms
