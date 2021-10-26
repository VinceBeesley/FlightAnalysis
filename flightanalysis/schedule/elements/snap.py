import numpy as np
from geometry import Transformation, scalar_projection
from flightanalysis import Section
    
from . import El



class Snap(El):
    def __init__(self, rolls: float, negative=False, l_tag=True, uid: str = None):
        super().__init__(uid)
        self.rolls = rolls
        self.negative = negative
        self.l_tag = l_tag

    def set_parameter(self, rolls=None, negative=None, l_tag=None):
        return Snap(
            rolls if rolls is not None else self.rolls,
            negative if negative is not None else self.negative,
            l_tag if l_tag is not None else self.l_tag,
            self.uid
        )

    def scale(self, factor):
        return self.set_parameter()

    def create_template(self, transform: Transformation, speed: float, simple: bool = False):
        el = Section.from_snap(
            transform, speed, self.rolls, self.negative, freq=1.0 if simple else None)
        return self._add_rolls(el, 0)

    def match_axis_rate(self, snap_rate: float, speed: float):
        return self.set_parameter()  # TODO should probably allow this somehow

    def match_intention(self, transform: Transformation, flown: Section):
        #TODO need to match flown pos/neg if F3A, not if IMAC
        return self.set_parameter(
            rolls=np.sign(np.mean(flown.gbrvel.x)) * abs(self.rolls)
        )
