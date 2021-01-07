


class Elements():
    LOOP = 0
    LINE = 1
    ROLL = 2
    SPIN = 3
    STALLTURN = 4
    SNAP = 5

    lookup = {
        "loop": LOOP,
        "line": LINE,
        "roll": ROLL,
        "spin": SPIN,
        "stallturn": STALLTURN,
        "snap": SNAP
    }


class Element():
    def __init__(self, classification: int, proportion: float):
        self.classification = classification
        self.proportion = proportion

    def from_dict(val):
        return Element(Elements.lookup[val["classification"]], val["proportion"])
