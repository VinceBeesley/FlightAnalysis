from flightanalysis.state import State
import numpy as np
from geometry import Point





def direction(self):
    if self.back_transform.rotate(Point(1, 0, 0)).x > 0:
        return "right"
    else:
        return "left"
