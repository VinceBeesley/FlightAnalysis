
from flightanalysis.schedule.figure_rules import Categories
from flightanalysis.schedule import Schedule, Manoeuvre, rollmaker, reboundrollmaker
from flightanalysis.schedule.elements import Line, Loop, Snap, Spin, StallTurn
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
        Line(0.5, 0.0),
        Loop(  0.3, -0.25),
    ] + rollmaker(2, "X", 4, 0.4, "Centre") + [
        Loop(  0.3, -0.25),
    ] + rollmaker(1, "/", 2, 0.4, "Centre") + [
        Loop(  0.3, 0.25),
    ] + rollmaker(2, "X", 4, 0.4, "Centre") + [
        Loop(  0.3, 0.25)   # 0.5
    ]),
    Manoeuvre("hsq", 2, [
        Line(0.2, 0.0),
        Loop(  0.3, 0.25),
    ] + rollmaker(1, "/", 2, 0.6, "Centre") + [
        Loop(  0.3, -0.25),
    ]),
    Manoeuvre("hump", 4, [
        Line(0.7, 0.0),
        Loop(  0.3, -0.25),
    ] +  reboundrollmaker([-1.0], 0.6, "Centre") + [
        Loop(  0.3, -0.5),
    ] + rollmaker(1, "/", 2, 0.6, "Centre") + [
        Loop(  0.3, 0.25),
    ]),
    Manoeuvre("hsc", 3, [
        Line(0.5, 0.0),
        Loop(  0.4, 0.125),
    ] + rollmaker(1, "/", 2, 0.25 / c45, "Centre") + [
        Loop(  0.4, -0.25),
    ] + rollmaker(1, "/", 2, 0.25 / c45, "Centre") + [
        Loop(  0.4, 0.125),  # 0.5, h=0.2
    ]),
    Manoeuvre("u45", 5, [
        Line(0.106586399182264974, 0.0, 0.0),
        Loop(  0.3, 0.125),
        Line(0.4, 0.0),
        Snap(1.5, negative=True),
        Line(0.4, 0.0),
        Loop(0.3, 0.125),
    ]),
    Manoeuvre("h8l", 3, [
        Line(0.28024080245320503, 0.0),
        Loop(0.3, 0.125),
        Line(0.16, 0.0),
        Loop(0.3, 0.125),
        Line(0.16, 0.0),
        Loop(0.3, 0.125),
        Line(0.16, 0.0),
        Loop(0.3, 0.125),  # 0.7
    ]),
    Manoeuvre("rc", 4, [
        Line(0.25, 0.0),  # 0.4
        Line(0.2, 0.5),  # 0.2
        Line(0.05, 0.0),
        Line(0.2, 0.5),
        Line(0.2, -0.5),
        Line(0.05, 0.0),
        Line(0.2, -0.5, 0.0),  # 0.45
    ]),
    Manoeuvre("imm", 2, [
        Line(0.15,  0.0),  # 0.6
        Loop(  0.697365440327093, 0.5),  # h=0.8
        Line(0.2, 0.5),  # 0.4
    ]),
    Manoeuvre("spin", 4, [
        Line(0.39320764389188684, 0.0, 0.0),
        Spin(2.5),
        Line(0.501698089027028, 0.0),
        Loop(  0.3, -0.25),  # 0.15, h=0.1
    ]),
    Manoeuvre("hB", 3, [
        Line(0.35, 0.0),  # 0.5
        Loop(  0.3, -0.25),  # 0.65
    ] + rollmaker(1, "/", 2, 0.5, "Centre") + [
        Loop(  0.3, -0.5),  # 0.95
    ] + rollmaker(1, "/", 2, 0.5, "Centre") + [
        Loop(  0.3, 0.25),  # 0.8
    ]),
    Manoeuvre("Et", 4, [
        Line(0.3428932188134527, 0.0),  # 0.5
        Loop(  0.5, 0.125),  # 0.65
    ] + reboundrollmaker([0.5, -0.5], 0.5, "Centre") + [
        Loop(  0.5, -7/8),  # 0.95
    ] + rollmaker(2, "X", 4, 0.3, "Centre") + [
        Loop(  0.5, 0.25),  # -0.18366018118654734, 0.9
    ]),
    Manoeuvre("hsq2", 2, [
        Line(0.35, 0.0),  # 0.6
        Loop(  0.3, 0.25),  # 0.65, 0.85
    ] + rollmaker(1, "/", 2, 0.5, "Centre") + [  # 0.25
        Loop(  0.3, -0.25),  # 0.6 , 0.1
    ]),
    Manoeuvre("figM", 5, [
        Line(0.45, 0.0),  # 0.15
        Loop(  0.3, -0.25),
    ] + reboundrollmaker([-0.75], 0.5, "Centre") + [
        StallTurn(),
        Line(0.5, 0.0),  # 0.15
        Loop(  0.3, 0.5),
        Line(0.5, 0.0),  # 0.15
        StallTurn(),
    ] + reboundrollmaker([-0.75], 0.5, "Centre") + [
        Loop(  0.3, -0.25),  # 0.15
    ]),
    Manoeuvre("fight", 2, [
        Line(0.2, 0.0),  # 0.25
        Loop(  0.3, -0.125),
    ] + reboundrollmaker([-0.25], 0.4, "Centre") + [
        Loop(  0.3, 0.5),
    ] + reboundrollmaker([0.25], 0.4, "Centre") + [
        Loop(  0.3, -0.125),  # 0.35
    ]),
    Manoeuvre("tri", 2, [
        Line(0.25, 0.0),  # 0.1
        Line(0.2, 0.5),  #0.1
        Line(0.3, 0.0),  #0.4
        Loop(  0.3, 0.375),  #0.4
        ] + rollmaker(2, "X", 4, 0.4/c45, "Centre") + [
        Loop(  0.3, -0.25),  #0.4
        ] + rollmaker(2, "X", 4, 0.4/c45, "Centre") + [
        Loop(  0.3, 0.375),  #0.4
        Line(0.3, 0.0),  #0.4
        Line(0.2, 0.5),  #0.1
    ]),
    Manoeuvre("shark", 2, [
        Line(0.75, 0.0),  # 0.9
        Loop(  0.3, -0.25),  #0.4
        ] + rollmaker(1, "/", 2, 0.25, "Centre") + [
        Loop(  0.3, 0.375),  #0.4
        ] + rollmaker(2, "X", 4, (0.25 + 2 * r1 * c45) / c45, "Centre") + [
        Loop(  0.3, 0.125),  #-0.17573593128807238
    ]),
    Manoeuvre("loop", 2, [
        Line(0.17573593128807238, 0.0, 0.0),  # 0.0
        Loop(  0.7, 0.375),  #0.4
        Loop(  0.7, 0.25, 0.5),  #0.4
        Loop(  0.7, -0.375),  #0.4
    ])
])
