
from flightanalysis.schedule.figure_rules import Categories
from flightanalysis.schedule import Schedule, Manoeuvre, rollmaker, reboundrollmaker
from flightanalysis.schedule.element import LineEl, LoopEl, SnapEl, SpinEl, StallTurnEl
import numpy as np


c45 = np.cos(np.radians(45))
mc45 = 1 - c45
r1 = 0.15
d1 = r1*2
r2 = 0.2
d2 = r2 * 2
r3 = 0.225
d3 = r3 * 2


p23 = Schedule("P23", Categories.F3A, "upright", -1.0, 0.1, [
    Manoeuvre("tophat", 4, [
        LineEl(0.5, 0.0),
        LoopEl(  0.3, -0.25),
    ] + rollmaker(2, "X", 4, 0.4, "Centre") + [
        LoopEl(  0.3, -0.25),
    ] + rollmaker(1, "/", 2, 0.4, "Centre") + [
        LoopEl(  0.3, 0.25),
    ] + rollmaker(2, "X", 4, 0.4, "Centre") + [
        LoopEl(  0.3, 0.25)   # 0.5
    ]),
    Manoeuvre("hsq", 2, [
        LineEl(0.2, 0.0),
        LoopEl(  0.3, 0.25),
    ] + rollmaker(1, "/", 2, 0.6, "Centre") + [
        LoopEl(  0.3, -0.25),
    ]),
    Manoeuvre("hump", 4, [
        LineEl(0.7, 0.0),
        LoopEl(  0.3, -0.25),
    ] +  reboundrollmaker([-1.0], 0.6, "Centre") + [
        LoopEl(  0.3, -0.5),
    ] + rollmaker(1, "/", 2, 0.6, "Centre") + [
        LoopEl(  0.3, 0.25),
    ]),
    Manoeuvre("hsc", 3, [
        LineEl(0.5, 0.0),
        LoopEl(  0.4, 0.125),
    ] + rollmaker(1, "/", 2, 0.25 / c45, "Centre") + [
        LoopEl(  0.4, -0.25),
    ] + rollmaker(1, "/", 2, 0.25 / c45, "Centre") + [
        LoopEl(  0.4, 0.125),  # 0.5, h=0.2
    ]),
    Manoeuvre("u45", 5, [
        LineEl(0.106586399182264974, 0.0, 0.0),
        LoopEl(  0.3, 0.125),
        LineEl(0.4, 0.0),
        SnapEl(0.05, 1.5),
        LineEl(0.4, 0.0),
        LoopEl(0.3, 0.125),
    ]),
    Manoeuvre("h8l", 3, [
        LineEl(0.28024080245320503, 0.0),
        LoopEl(0.3, 0.125),
        LineEl(0.16, 0.0),
        LoopEl(0.3, 0.125),
        LineEl(0.16, 0.0),
        LoopEl(0.3, 0.125),
        LineEl(0.16, 0.0),
        LoopEl(0.3, 0.125),  # 0.7
    ]),
    Manoeuvre("rc", 4, [
        LineEl(0.25, 0.0),  # 0.4
        LineEl(0.2, 0.5),  # 0.2
        LineEl(0.05, 0.0),
        LineEl(0.2, 0.5),
        LineEl(0.2, -0.5),
        LineEl(0.05, 0.0),
        LineEl(0.2, -0.5, 0.0),  # 0.45
    ]),
    Manoeuvre("imm", 2, [
        LineEl(0.15,  0.0),  # 0.6
        LoopEl(  0.697365440327093, 0.5),  # h=0.8
        LineEl(0.2, 0.5),  # 0.4
    ]),
    Manoeuvre("spin", 4, [
        LineEl(0.39320764389188684, 0.0, 0.0),
        SpinEl(0.05, 2.5),
        LineEl(0.501698089027028, 0.0),
        LoopEl(  0.3, -0.25),  # 0.15, h=0.1
    ]),
    Manoeuvre("hB", 3, [
        LineEl(0.35, 0.0),  # 0.5
        LoopEl(  0.3, -0.25),  # 0.65
    ] + rollmaker(1, "/", 2, 0.5, "Centre") + [
        LoopEl(  0.3, -0.5),  # 0.95
    ] + rollmaker(1, "/", 2, 0.5, "Centre") + [
        LoopEl(  0.3, 0.25),  # 0.8
    ]),
    Manoeuvre("Et", 4, [
        LineEl(0.3428932188134527, 0.0),  # 0.5
        LoopEl(  0.5, 0.125),  # 0.65
    ] + reboundrollmaker([0.5, -0.5], 0.5, "Centre") + [
        LoopEl(  0.5, -7/8),  # 0.95
    ] + rollmaker(2, "X", 4, 0.3, "Centre") + [
        LoopEl(  0.5, 0.25),  # -0.18366018118654734, 0.9
    ]),
    Manoeuvre("hsq2", 2, [
        LineEl(0.35, 0.0),  # 0.6
        LoopEl(  0.3, 0.25),  # 0.65, 0.85
    ] + rollmaker(1, "/", 2, 0.5, "Centre") + [  # 0.25
        LoopEl(  0.3, -0.25),  # 0.6 , 0.1
    ]),
    Manoeuvre("figM", 5, [
        LineEl(0.45, 0.0),  # 0.15
        LoopEl(  0.3, -0.25),
    ] + reboundrollmaker([-0.75], 0.5, "Centre") + [
        StallTurnEl(),
        LineEl(0.5, 0.0),  # 0.15
        LoopEl(  0.3, 0.5),
        LineEl(0.5, 0.0),  # 0.15
        StallTurnEl(),
    ] + reboundrollmaker([-0.75], 0.5, "Centre") + [
        LoopEl(  0.3, -0.25),  # 0.15
    ]),
    Manoeuvre("fight", 2, [
        LineEl(0.2, 0.0),  # 0.25
        LoopEl(  0.3, -0.125),
    ] + reboundrollmaker([-0.25], 0.4, "Centre") + [
        LoopEl(  0.3, 0.5),
    ] + reboundrollmaker([0.25], 0.4, "Centre") + [
        LoopEl(  0.3, -0.125),  # 0.35
    ]),
    Manoeuvre("tri", 2, [
        LineEl(0.25, 0.0),  # 0.1
        LineEl(0.2, 0.5),  #0.1
        LineEl(0.3, 0.0),  #0.4
        LoopEl(  0.3, 0.375),  #0.4
        ] + rollmaker(2, "X", 4, 0.4/c45, "Centre") + [
        LoopEl(  0.3, -0.25),  #0.4
        ] + rollmaker(2, "X", 4, 0.4/c45, "Centre") + [
        LoopEl(  0.3, 0.375),  #0.4
        LineEl(0.3, 0.0),  #0.4
        LineEl(0.2, 0.5),  #0.1
    ]),
    Manoeuvre("shark", 2, [
        LineEl(0.75, 0.0),  # 0.9
        LoopEl(  0.3, -0.25),  #0.4
        ] + rollmaker(1, "/", 2, 0.25, "Centre") + [
        LoopEl(  0.3, 0.375),  #0.4
        ] + rollmaker(2, "X", 4, (0.25 + 2 * r1 * c45) / c45, "Centre") + [
        LoopEl(  0.3, 0.125),  #-0.17573593128807238
    ]),
    Manoeuvre("loop", 2, [
        LineEl(0.17573593128807238, 0.0, 0.0),  # 0.0
        LoopEl(  0.7, 0.375),  #0.4
        LoopEl(  0.7, 0.25, 0.5),  #0.4
        LoopEl(  0.7, -0.375),  #0.4
    ])
])
