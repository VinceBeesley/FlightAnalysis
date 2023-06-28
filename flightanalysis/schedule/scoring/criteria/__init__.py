from __future__ import annotations


class Criteria:
    pass

    @classmethod
    def from_dict(Cls, data):
        for Child in Cls.__subclasses__():
            if Child.__name__ == data["kind"]:
                return Child.from_dict(data)
        raise ValueError("unknown criteria")


from .single import Single
from .continuous import Continuous
from .comparison import Comparison
from .combination import Combination

from . import f3a

