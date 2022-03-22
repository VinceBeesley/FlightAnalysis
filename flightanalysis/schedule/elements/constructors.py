import numpy as np
from geometry import Point
from flightanalysis.state import State

from . import Line, Loop, Snap, Spin, StallTurn


def get_rates(flown: State):
    
    return {
        Loop: np.percentile(abs(flown.rvel.y), 90),
        Line: np.percentile(abs(flown.rvel.x), 95),
        Snap: max(abs(flown.rvel.x)),
        StallTurn: np.percentile(abs(flown.rvel.z), 99.9),
        Spin: np.percentile(abs(flown.rvel.x), 99.5),
        "speed": flown.vel.x.mean(),
        "distance": flown.pos.y.mean(),
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
        elms = [Line(rlength * num / denom, direction * num / denom, l_tag)]
    elif arg == "X":
        elms = []
        for i in range(num):
            lsum += rlength / denom
            elms.append(Line(rlength / denom, direction / denom, l_tag))
            if i < num - 1:
                elms.append(Line(0.05, 0.0))
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
            elms.append(Line(0.05, 0.0, l_tag))
            lsum += 0.05
        last_dir = np.sign(roll)
        if snap:
            elms.append(Snap(roll))
        else:
            elms.append(Line(rlength * abs(roll), roll, l_tag))
        lsum += rlength * abs(roll)
    return paddinglines(position, length, lsum, elms, l_tag)


def rollsnapcombomaker(rolls: list, length: float, position="Centre", rlength=0.3, l_tag=True, bounce=True):
    lsum = 0.0
    elms = []
    last_dir = -np.sign(rolls[0][1])
    for roll in rolls:
        # add pause if roll in same direction
        if last_dir == np.sign(roll[1]) or not bounce:
            elms.append(Line(0.05, 0.0, l_tag))
            lsum += 0.05
        last_dir = np.sign(roll[1])
        if roll[0] == "snap":
            elms.append(Snap(roll[1]))
            lsum += 0.05 * abs(roll[1])
        if roll[0] == "roll":
            elms.append(Line(rlength * abs(roll[1]), roll[1], l_tag))
            lsum += rlength * abs(roll[1])
    return paddinglines(position, length, lsum, elms, l_tag)


def paddinglines(position, length, lsum, elms, l_tag=True):
    lleft = length - lsum
    if position.lower() == "centre":
        return [
            Line(lleft / 2, 0.0, l_tag)
        ] + elms + [
            Line(lleft / 2, 0.0, l_tag)
        ]
    elif position.lower() == "start":
        return elms + [Line(lleft, 0.0)]
    elif position.lower() == "end":
        return [Line(lleft, 0.0)] + elms
    elif position == "None":
        return elms