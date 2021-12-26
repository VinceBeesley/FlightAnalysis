from geometry import Point



class ACConstants:
    def __init__(self, s: float, c:float, b:float, mass:float, cg:Point):
        self.s = s
        self.c = c
        self.b = b
        self.mass = mass
        self.cg = cg



#TODO this needs to be stored somewhere else:
cold_draft = ACConstants(0.569124, 0.31211, 1.8594, 4.5, Point(0.6192,0.0,0.0))
