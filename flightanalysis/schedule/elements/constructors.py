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
    
    out_rolls = []
    tlen=0.0
    for i, roll in enumerate(rolls):
        rlen = roll.rate * speed * abs(roll.amount) * 2 * np.pi
        out_rolls.append(Line(speed, rlen, roll.amount))
        tlen += rlen
        if not i == len(rolls)-1:
            out_rolls.append(Line(speed, pause))
            tlen = tlen + pause

    lleft = length - tlen
    assert lleft > 0

    if position == RollPosition.CENTRE:
        return [Line(speed, lleft/2)] + out_rolls + [Line(speed, lleft/2)]
    elif position == RollPosition.START:
        return out_rolls + [Line(speed, lleft)]
    elif position == RollPosition.END:
        return [Line(speed, lleft)] + out_rolls
   

def roll(rollstring, speed, length, pause, rate, position):
    if rollstring[1] == "/":
        return rollcombo(
            [Roll(int(rollstring[0])/int(rollstring[2]), rate)],
            speed, length, pause, position
        )
    elif rollstring[1] == "X":
        return rollcombo(
            [Roll(1/int(rollstring[2]), rate) for _ in range(int(rollstring[0]))],
            speed, length, pause, position
        )
