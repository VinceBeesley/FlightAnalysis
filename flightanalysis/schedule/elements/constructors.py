import numpy as np
from geometry import Point
from flightanalysis.state import State
from enum import Enum
from . import Line, Loop, Snap, Spin, StallTurn
from collections import namedtuple
from typing import List


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


class RollPosition(Enum):
    CENTRE=0
    START=1
    END=2
    ENTIRE=3

class RollKind(Enum):
    ROLL=0
    SNAP=1

class Roll():
    def __init__(self, amount, rate: float, kind:RollKind=RollKind.ROLL):
        self.kind = kind
        self.amount = amount
        self.rate = rate

def rollcombo(rolls: List[Roll], speed, length: str, pause:str, position:RollPosition=RollPosition.CENTRE):
    
    def make_rolls(rolls, pause):
        out_rolls = []
        for roll in rolls:
            out_rolls.append(Line(speed, roll.rate * speed * abs(roll.amount), roll.amount)),
            out_rolls.append(Line(speed, pause))
        return out_rolls

    def pad_rolls(elms: List[Line], speed, length, position):
        pass

    return pad_rolls(make_rolls(rolls, pause), speed, length, position)

    


    
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