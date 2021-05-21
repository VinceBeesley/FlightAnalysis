
from typing import Dict
from enum import Enum
from uuid import uuid4

class ElClass(Enum):
    LINE = 0
    LOOP = 1
    KELOOP = 2
    SPIN = 4
    STALLTURN = 5
    SNAP = 6
    
class Element():
    def __init__(self, classification: ElClass, size: float, roll: float, loop: float):
        self.classification = classification
        self.size = size
        self.roll = roll
        self.loop = loop


    def from_dict(val):
        return Element(ElClass[val["classification"]], val["size"], val["roll"], val["loop"])



def rollmaker(num: int, arg: str, denom: float, length: float=0.5, position="Centre", right=False):
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
        lsum += 0.4 * num / denom
        elms = [Element(ElClass.LINE,  0.4 * num / denom, direction * num / denom, 0.0)]
    elif arg == "X":
        elms = []
        for i in range(num):
            lsum += 0.4 / denom
            elms.append(Element(ElClass.LINE,  0.4 / denom, direction / denom, 0.0))
            if i < num-1:
                elms.append(Element(ElClass.LINE,  0.05, 0.0, 0.0))
                lsum += 0.05
    else:
        raise KeyError
    return paddinglines(position, length, lsum, elms)

def reboundrollmaker(rolls:list, length: float=0.5, position="Centre"):
    lsum = 0.0
    elms = []
    for roll in rolls:
        elms.append(Element(ElClass.LINE,  0.4 * abs(roll), roll, 0.0))
        lsum += 0.4 * abs(roll)
    return paddinglines(position, length, lsum, elms)

def paddinglines(position, length, lsum, elms):
    lleft = length - lsum
    if position == "Centre":
        return [
            Element(ElClass.LINE,  lleft / 2, 0.0, 0.0)
        ] + elms + [
            Element(ElClass.LINE,  lleft / 2, 0.0, 0.0)
        ]
    elif position=="Start":
        return elms  + [Element(ElClass.LINE,  lleft, 0.0, 0.0)]
    elif position == "End":
        return [Element(ElClass.LINE,  lleft, 0.0, 0.0)] + elms
    