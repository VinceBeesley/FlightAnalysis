
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
