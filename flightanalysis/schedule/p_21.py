

from flightanalysis import schedule
from flightanalysis.schedule import Schedule, Manoeuvre, rollmaker
from flightanalysis.schedule.figure_rules import Categories
from flightanalysis.schedule.element import LineEl, LoopEl, SnapEl, SpinEl, StallTurnEl
from flightanalysis.schedule.figure_rules import F3AEnd, F3ACentre, F3AEndB
import numpy as np


c45 = np.cos(np.radians(45))
mc45 = 1 - c45
r1 = 0.15
d1 = r1*2
r2 = 0.2
d2 = r2 * 2
r3 = 0.225
d3 = r3 * 2

p21 = Schedule("P21", Categories.F3A, "inverted", -1.0, 0.55, [
    Manoeuvre("v8", 3, [
        LineEl(0.8, 0.0),
        LineEl(0.2, 0.5),
        LoopEl(0.45, 1.0),
        LoopEl(0.45, -1.0),
        LineEl(0.2, 0.5),
    ], F3ACentre),
    Manoeuvre("stall", 3, [
        LineEl(0.3, 0.0),
        LoopEl(0.3, 0.25),
        LineEl(0.25, 0.0),
        StallTurnEl()
    ] + rollmaker(2, "X", 4, 0.7, "Centre") + [
        LoopEl(0.3, -0.25)
    ], F3AEnd),
    Manoeuvre("sqL", 4, [
        LineEl(0.5, 0.0),
        LoopEl(0.4, -0.125),
        LineEl(0.3, 0.0),
        LoopEl(0.4, -0.25)
    ] + rollmaker(1, "/", 2, 0.3, "Centre") + [
        LoopEl(0.4, 0.25),
        LineEl(0.3, 0.0),
        LoopEl(0.4, 0.25)
    ] + rollmaker(1, "/", 2, 0.3, "Centre") + [
        LoopEl(0.4, -0.125)
    ], F3ACentre),
    Manoeuvre("9", 4, [
        LineEl(0.35, 0.0),
        LoopEl(0.4, -0.25),
        LineEl(0.05, 0.0),
        LineEl(0.2, 0.5),
        LineEl(0.2, -0.5),
        LineEl(0.05, 0.0),
        LoopEl(0.4, 0.75),
    ], F3AEnd),  # 0.35+0.2+0.2 = 0.75, h =0.1+0.2+ 0.5 -0.2=0.6
    Manoeuvre("ke", 5, [
        LineEl(0.25,  0.0),  # 0.5
        LineEl(0.1, 0.25),  # 0.4
        LineEl(0.2, -0.5),  # 0.2
        LineEl(0.4, 0.0),  # -0.2
        LineEl(0.2, -0.5),  # -0.4
        LineEl(0.1, 0.25)  # -0.5
    ], F3ACentre
    ),
    Manoeuvre("sS", 2, [
        LineEl(0.25, 0.0),  # -0.75
        LoopEl(0.5, 0.5),  # h=0.1
        LineEl(0.15, 0.5),  # -0.6
        LineEl(0.05, 0.0),  # -0.55
        LineEl(0.15, 0.5)  # -0.4
    ], F3AEnd
    ),
    Manoeuvre("golf", 5, [
        LineEl(0.12, 0.0),
        LoopEl(0.45, 0.125),
        LineEl(0.28 / c45, 0.0),
        LoopEl(0.45, 0.125),
        LoopEl(0.45, 0.5, 0.5),
        LoopEl(0.45, -0.125),
        LineEl(0.28 / c45, 0.0),
        LoopEl(0.45, -0.125)
    ], F3ACentre
    ),
    Manoeuvre("sFin", 3, [
        LineEl(0.57, 0.0),
        LoopEl(d1, -0.25),
        LineEl(0.25, 0.0),
        LoopEl(d1, -0.375)
    ] + rollmaker(2, "X", 4,
                  (0.25 + 2 * r1 * c45) / c45,
                  "Centre") + [
        LoopEl(0.3, -0.125)  # 1 - r1 - l1 - 2rc45
    ], F3AEnd
    ),
    Manoeuvre("dImm", 5, [
        LineEl(1.1 - 0.25 - r1 - 4 * r1 * c45, 0.0),  # 0.1
        LineEl(0.2, 0.5),
        LoopEl(0.6,  0.5),
    ] + rollmaker(4, "X", 8, 0.6, "Start") + [
        LoopEl(0.6,  -0.5),
        LineEl(0.2,  0.5)  # 0.1
    ], F3ACentre
    ),
    Manoeuvre("hB", 3, [
        LineEl(0.55,  0.0),  # 0.45
        LoopEl(0.3,  0.25),  # 0.6
    ] + rollmaker(1, "/", 2, 0.5, "Centre") + [
        LoopEl(0.3,  0.5),  # 0.9
        LineEl(0.5,  0.0),
        LoopEl(0.3,  0.25)  # 0.75
    ], F3AEnd
    ),
    Manoeuvre("rollC", 3, [
        LineEl(0.35,  0.0),  # 0.4
        LineEl(0.2,  0.5),  # -0.2
        LineEl(0.4,  -1.0),  # +0.2
        LineEl(0.2,  0.5)  # +0.4
    ], F3ACentre
    ),
    Manoeuvre("tHat", 3, [
        LineEl(0.395,  0.0),  # 0.795
        LoopEl(0.3,  0.25),
    ] + rollmaker(1, "/", 2, 0.5, "Centre") + [
        LoopEl(0.3,  -0.25),
        LineEl(0.3182076438918871,  0.0),  # 0.46320764389188707
        SpinEl(0.05,  2.5),  # [0.47, 0.5637655569733979, 0.8516980890270289]
        LineEl(0.601698089027029,  0.0),
        LoopEl(0.3,  -0.25)  # 0.27
    ], F3AEnd
    ),
    Manoeuvre("Z", 3, [
        LineEl(0.37,  0.0),  # 0.05
        LoopEl(d1,  -0.375),
    ] + rollmaker(1, "/", 1, 2 * (0.05 + r1 * c45) / c45, "Centre") + [
        LoopEl(d1,  0.375)  # 0.05, h=0.9242640687119287
    ], F3ACentre
    ),
    Manoeuvre("com", 3, [
        LineEl(0.325,  0.0),  # 0.275
        LoopEl(0.3,  0.125),
        LineEl(0.15,  0.0),
        LineEl(0.1,  0.25),
        LineEl(0.1,  -0.25),
        LineEl(0.15,  0.0),
        LoopEl(0.3,  -0.75),
        LineEl(0.15,  0.0),
        LineEl(0.2,  0.5),
        LineEl(0.15,  0.0),
        LoopEl(0.3,  -0.125)  # 0.275
    ], F3AEndB
    ),
    Manoeuvre("4pt", 3, [
        LineEl(0.06,  0.0),  # 0.21
        LineEl(0.07,  0.25),
        LineEl(0.05,  0.0),
        LineEl(0.07,  0.25),
        LineEl(0.05,  0.0),
        LineEl(0.07,  0.25),
        LineEl(0.05,  0.0),
        LineEl(0.07,  0.25)  # 0.21, h=0.34142135623730985
    ], F3ACentre
    ),
    Manoeuvre("hsq", 3, [
        LineEl(0.2,  0.0),
        LoopEl(0.3,  -0.125),
    ] + rollmaker(1, "/", 4, 0.24, "Centre") + [
        LoopEl(0.3, -0.25, 0.0, True),
    ] + rollmaker(1, "/", 4, 0.24, "Centre", True) + [
        LoopEl(0.3,  -0.125)
    ], F3AEndB
    ),
    Manoeuvre("aV", 3, [
        LineEl(0.4399999999999997,  0.0),
        LoopEl(0.7,  -0.5),
        SnapEl(0.05,  1.0),
        LoopEl(0.7,  -0.5)
    ], F3ACentre
    ),
    Manoeuvre("Land", 0, [
        LineEl(0.2, 0.0)
    ], F3AEnd)
])
