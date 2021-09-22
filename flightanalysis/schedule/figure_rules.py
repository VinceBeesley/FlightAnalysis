from enum import Enum


class Categories(Enum):
    F3A = 0
    IMAC = 1
    IAC = 2

    lookup = {
        "F3A": F3A,
        "IMAC": IMAC,
        "IAC": IAC
    }

class Rules:
    pass

class IMAC(Rules):  # TODO extend to cover categories
    line_lengths = True # Except where l_tag is False
    loop_diameter = True #Except where r_tag is False
    centering = False
    roll_rate = True #
    roll_centering = True
    
class F3AEnd(Rules):
    line_lengths = True
    loop_diameter = True
    centering = False
    roll_rate = True
    roll_centering = True

class F3AEndB(Rules):
    line_lengths = True
    loop_diameter = True
    centering = False
    roll_rate = True
    roll_centering = True

class F3ACentre(Rules):
    line_lengths = True
    loop_diameter = True
    centering = True
    roll_rate = True
    roll_centering = True

rules = dict(
    IMAC=IMAC,
    F3AEnd=F3AEnd,
    F3AEndB=F3AEndB,
    F3ACentre=F3ACentre
)