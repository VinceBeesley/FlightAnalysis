
from typing import Dict
from enum import Enum
from uuid import uuid4
import numpy as np
from geometry import Transformation, Point, scalar_projection, Points, scalar_projection
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

    def scale(self, factor):
        el = LineEl(self.length * factor, self.rolls)
        el.uid = self.uid
        return el

    def create_template(self, transform: Transformation, speed: float):
        el = Section.from_line(transform, speed, self.length)
        return self._add_rolls(el, self.rolls)

    def resize(self, sec: Section, transform: Transformation):
        return LineEl(
            scalar_projection(
                sec.get_state_from_index(-1).pos -
                sec.get_state_from_index(0).pos,
                transform.rotate(Point.X())
            ),
            self.rolls
        )

    def match_axis_rate(self, roll_rate: float, speed: float):
        # roll rate in radians per second, speed in m / s
        if not self.rolls == 0.0:
            el = LineEl(2 * np.pi * abs(self.rolls) *
                        speed / roll_rate, self.rolls)
        else:
            el = LineEl(self.length, self.rolls)
        el.uid = self.uid
        return el

    def match_intention(self, transform: Transformation, flown: Section):
        #TODO this is just an idea, better to somehow specify externally the higher
        #level parameters that should be met
        new_transform = Transformation(
            flown.get_state_from_index(0).pos,
            transform.rotation
        )
        length = scalar_projection(
            flown.get_state_from_index(-1).pos - new_transform.translation,
            new_transform.rotate(Point(1, 0, 0))
        )
        return LineEl(length, np.sign(np.mean(Points.from_pandas(flown.brvel).x)) * abs(self.rolls))


class LoopEl(El):
    def __init__(self, diameter: float, loops: float, rolls=0.0, ke: bool = False):
        super().__init__()
        self.loops = loops
        self.diameter = diameter
        self.rolls = rolls
        self.ke = ke

    def scale(self, factor):
        el = LoopEl(self.diameter * factor, self.loops, self.rolls, self.ke)
        el.uid = self.uid
        return el

    def create_template(self, transform: Transformation, speed: float):
        el = Section.from_loop(transform, speed, self.loops,
                               0.5 * self.diameter, self.ke)
        return self._add_rolls(el, self.rolls)

    def match_axis_rate(self, pitch_rate: float, speed: float):
        el = LoopEl(
            2 * speed / pitch_rate,
            self.loops,
            self.rolls,
            self.ke
        )
        el.uid = self.uid
        return el

    def resize(self, sec: Section, transform: Transformation):
        pos = transform.rotate(Points.from_pandas(sec.pos))

        _x = pos.x
        _y = pos.y if self.ke else pos.z

        def calc_R(xc, yc): return np.sqrt((_x - xc)**2 + (_y - yc)**2)

        def f_2(c):
            Ri = calc_R(*c)
            return Ri - Ri.mean()

        center_2, ier = optimize.leastsq(f_2, (_x.mean(), _y.mean()))
        Ri_2 = calc_R(*center_2)

        return LoopEl(2 * Ri_2.mean(), self.loops, self.rolls, self.ke)

    def match_intention(self, transform: Transformation, flown: Section):
        new_transform = Transformation(
            flown.get_state_from_index(0).pos,
            transform.rotation
        )
        #TODO match average radius and starting point, fix errors



class SpinEl(El):
    _speed_factor = 1 / 10

    def __init__(self, length: float, turns: float, opp_turns: float = 0.0):
        super().__init__()
        self.length = length
        self.turns = turns
        self.opp_turns = opp_turns

    def scale(self, factor):
        el = SpinEl(self.length * factor, self.turns, self.opp_turns)
        el.uid = self.uid
        return el

    def _create_template(self, transform: Transformation, speed: float):
        el = Section.from_spin(transform, self.length,
                               self.turns, self.opp_turns)
        return self._add_rolls(el, 0.0)

    def create_template(self, transform: Transformation, speed: float):
        _inverted = np.sign(transform.rotate(Point(0, 0, 1)).z)

        nose_drop = Section.from_loop(
            transform, 5.0, -0.25 * _inverted, 2.0, False)
        nose_drop.data["sub_element"] = "nose_drop"

        rotation = Section.from_line(
            nose_drop.get_state_from_index(-1).transform,
            speed * self._speed_factor,
            self.length * self.turns / (self.turns + self.opp_turns)
        ).superimpose_roll(self.turns)
        rotation.data["sub_element"] = "rotation"

        if self.opp_turns == 0.0:
            sec = Section.stack([nose_drop, rotation])
        else:
            rotation2 = Section.from_line(
                rotation.get_state_from_index(-1).transform,
                speed * self._speed_factor,
                self.length * self.opp_turns / (self.turns + self.opp_turns)
            ).superimpose_roll(self.opp_turns)

            rotation2.data["sub_element"] = "opp_rotation"

            sec = Section.stack([nose_drop, rotation, rotation2])
        return self._add_rolls(sec, 0.0)

    def match_axis_rate(self, spin_rate, speed: float):
        #LineEl(2 * np.pi * self.rolls * speed / roll_rate, self.rolls)
        return SpinEl(
            2 * np.pi * (abs(self.turns) + abs(self.opp_turns)) * speed *
            SpinEl._speed_factor / spin_rate,
            self.turns,
            self.opp_turns
        )


class SnapEl(El):
    def __init__(self, length: float, rolls: float):
        super().__init__()
        self.length = length
        self.rolls = rolls

    def scale(self, factor):
        el = SnapEl(self.length * factor, self.rolls)
        el.uid = self.uid
        return el

    def create_template(self, transform: Transformation, speed: float):
        el = Section.from_line(transform, speed, self.length)
        return self._add_rolls(el, self.rolls)

    def match_axis_rate(self, snap_rate: float, speed: float):
        el = SnapEl(2 * np.pi * abs(self.rolls) *
                    speed / snap_rate, self.rolls)
        el.uid = self.uid
        return el


class StallTurnEl(El):
    _speed_scale = 1 / 20

    def __init__(self, direction: int = 1, width: float = 1.0):
        super().__init__()
        self.direction = direction
        self.width = width

    def scale(self, factor):
        # TODO dont scale this element? good idea?
        el = StallTurnEl(self.direction, self.width)
        el.uid = self.uid
        return el

    def create_template(self, transform: Transformation, speed: float):
        el = Section.from_loop(
            transform,
            StallTurnEl._speed_scale * speed,
            0.5 * self.direction,
            self.width / 2,
            True)
        return self._add_rolls(el, 0.0)

    def match_axis_rate(self, yaw_rate: float, speed: float):
        el = StallTurnEl(
            self.direction,
            2 * StallTurnEl._speed_scale * speed / yaw_rate
        )
        el.uid = self.uid
        return el


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
            elms.append(LineEl(rlength / denom, direction / denom))
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
            elms.append(LineEl(rlength * abs(roll[1]), roll[1]))
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
