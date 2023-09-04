from __future__ import annotations
import numpy as np
from dataclasses import dataclass
from .. import Criteria


@dataclass
class Single(Criteria):

    def __call__(self, ids, values):
        return ids, self.lookup(np.array(values))
