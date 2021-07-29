


class Categories():
    F3A = 0
    IMAC = 1
    IAC = 2

    lookup = {
        "F3A": F3A,
        "IMAC": IMAC,
        "IAC": IAC
    }


class IMAC:  # TODO extend to cover categories
    line_lengths = True
    loop_diameter = False
    centering = False
    roll_centering = True
    
class F3AEnd:
    line_lengths = False
    loop_diameter = True
    centering = False
    roll_centering = True

class F3AEndB:
    line_lengths = True
    loop_diameter = True
    centering = False
    roll_centering = True

class F3ACentre:
    line_lengths = True
    loop_diameter = True
    centering = True
    roll_centering = True