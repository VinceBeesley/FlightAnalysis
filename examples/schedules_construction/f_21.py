

from flightanalysis.schedule import Schedule, Manoeuvre, rollmaker, reboundrollmaker, rollsnapcombomaker
from flightanalysis.schedule.element import LoopEl, LineEl, SnapEl, SnapEl, SpinEl, StallTurnEl
from flightanalysis.schedule.figure_rules import Categories, F3ACentre, F3AEndB, F3AEnd
import numpy as np

c45 = np.cos(np.radians(45))
mc45 = 1 - c45
r1 = 0.15
d1 = r1*2
r2 = 0.25
d2 = r2 * 2

r3 = 0.21
d3 = r3 * 2


f21 = Schedule("F21", Categories.F3A, "upright", -1.0, 0.15, [
    Manoeuvre("golf", 4, [
        LineEl(1.081066, 0.0),
        LoopEl(d1, -3/8),
    ] + rollmaker(3, "/", 4, 0.45, "Centre") + [
        LoopEl(d1, -3/8,ke=True),
        SnapEl(0.05, 1.0, l_tag=False),
        LoopEl(d1, -3/8, ke=True),
    ] + rollmaker(3, "/", 4, 0.45, "Centre", right=True) + [
        LoopEl(d1, -3/8),
    ], F3ACentre),
    Manoeuvre("cub8", 3, [
        LineEl(0.1, 0.0),
        LoopEl(d2, -1/8),
    ] + reboundrollmaker([0.25, 0.25, -0.25], 2*r2, "Centre") + [
        LoopEl(d2, 5/8, ke=True),
        LineEl(0.3, 0.75),
    ], F3AEnd),
    Manoeuvre("circle", 4, [
        LineEl(0.4260407468305834, 0.0),
        LoopEl(0.7, -0.5, 1/2, True),
        LoopEl(0.7, 0.5, -1/2, True),
    ], F3ACentre),
    Manoeuvre("tHat", 4, [
        LineEl(0.4, 0.0),
        LoopEl(d1, 0.25),
    ] + rollmaker(3, "X", 4, 0.5, "Centre", right=False, l_tag=False) + [
        LoopEl(d1, -0.25),
        LineEl(0.1, 0.0, l_tag=False),
        LoopEl(d1, -0.25),
    ] + reboundrollmaker([3/4], 0.5, "Centre",rlength=0.05, snap=True, l_tag=False) + [
        LoopEl(d1, -0.25),
    ], F3AEnd),
    Manoeuvre("hB", 5, [
        LineEl(0.2, 0.0),
        LoopEl(d1+0.1, -0.25, -0.25),
    ] + rollmaker(1, "/", 1, 0.5, "Centre", right=False) + [
        LoopEl(d1+0.1, 0.5),
    ] + reboundrollmaker([0.5, -0.5], 0.5, "Centre") + [
        LoopEl(d1+0.1, -0.25, 0.25, ke=True),
    ], F3ACentre),
    Manoeuvre("v8", 5, [
        LineEl(0.3, 0.0),
        LoopEl(d3, 3/8),
        LoopEl(d3,  1/8, 0.25),
        LoopEl(d3,  -1/8, 0.25, ke=True),
        LoopEl(d3, 7/8),
    ], F3AEnd),
    Manoeuvre("stall", 4, [
        LineEl(0.5+r3 - 0.006792356108113501, 0.0),
        LoopEl(d3, -3/4),
    ] + reboundrollmaker([0.25, -0.5], 0.6, "Centre") + [
        StallTurnEl( 1, 0.05),
    ] + rollmaker(3, "/", 4, 0.6, "Centre", right=False) + [
        LoopEl(d3, 3/4),
    ], F3ACentre),
    Manoeuvre("9", 4, [
        LineEl(1.0396229316756604 + 0.006792356108113501, 0.0),
        LoopEl(d1, -3/4),
        LineEl(0.16, 0.0),
        SnapEl(0.1, 1.5),
        LineEl(0.16, 0.0),
        LoopEl(d1, -1/4),
    ], F3AEnd),
    Manoeuvre("tHat2", 6, [
        LineEl(0.05, 0.0),
        LoopEl(d1, -1/4),
    ] + rollmaker(3, "/", 4, 0.4, "Centre", right=False, rlength=0.3) + [
        LoopEl(d1, -1/4, ke=True),
    ] + rollmaker(1, "/", 1, 0.4, "Centre", right=False, rlength=0.3, l_tag=False) + [
        LoopEl(d1, -1/4, ke=True),
    ] + rollmaker(1, "/", 4, 0.4, "Centre", right=False, rlength=0.3) + [
        LoopEl(d1, -1/4),
    ], F3ACentre),
    Manoeuvre("hSqL", 3, [
    ] + rollmaker(1, "/", 2, 0.35, "End", right=False, rlength=0.3) + [
        LoopEl(d1, 1/4),
    ] + reboundrollmaker([0.5, -1.0], 0.55, "Centre", rlength=0.3) + [
        LoopEl(d1, -1/4),
    ], F3AEnd),
    Manoeuvre("45Line", 6, [
        LineEl(0.35 + 0.012867965644036, 0.0),
        LoopEl(d1, -1/8),
    ] + rollsnapcombomaker([
        ("roll", 0.25),
        ("snap", 1.0),
        ("snap", -1.0),
        ("roll", -0.25)], (0.85 - 2*r1*mc45) / c45, "Centre", rlength=0.4) + [
        LoopEl(d1, 1/8),
    ], F3ACentre),
    Manoeuvre("8loop", 3, [
        LineEl(0.05, 0.0),
        LoopEl(d1, 1/8),
    ] + rollmaker(1, "/", 2, 0.2, "Centre", right=False, rlength=0.3) + [
        LoopEl(d1, -1/8),
        LineEl(0.2, 0.0),
        LoopEl(d1, -1/8),
    ] + rollmaker(1, "/", 2, 0.2, "Centre", right=False, rlength=0.3) + [
        LoopEl(d1, 1/8),
    ], F3AEnd),
    Manoeuvre("loop", 5, [
        LineEl(0.5371320343559636, 0.0),
        LoopEl(0.782842712474619, 1/2, 1.0),
        LoopEl(0.782842712474619, 1/2, -1.0),
    ], F3ACentre),
    Manoeuvre("spin", 3, [
        LineEl(0.95, 0.0),
        SpinEl(0.06, 2.5),
        LineEl(0.5745408015016459),
        LoopEl(d1, -0.25),
    ], F3AEnd),
    Manoeuvre("rollC", 3,
        reboundrollmaker([0.5,-0.25, -0.25, -0.25, -0.25, 0.5], 1.1885847122162254, "End", rlength=0.3),
        F3ACentre
    ),
    Manoeuvre("fTurn", 4, [
        LineEl(0.1, 0.0),
        LoopEl(d1, -1/8),
        ] + rollmaker(3, "/", 4, 0.4, "Centre", right=False, rlength=0.3) + [
        LoopEl(d1, 0.5),
        ] + reboundrollmaker([-0.75], 0.4, "Centre", rlength=0.05, snap=True) + [
        LoopEl(d1, -1/8),
    ], F3AEnd),
    Manoeuvre("square", 4, [
        LineEl(0.475 - 0.05),
        LineEl(0.1, -0.25),
        LineEl(0.15, 0.0),
        LoopEl(d1, 1/4),
        ] + rollmaker(1, "/", 2, 0.4, "Centre", right=False, rlength=0.3) + [
        LoopEl(d1, -1/4),
        ] + rollmaker(1, "/", 2, 0.4, "Centre", right=False, rlength=0.3) + [
        LoopEl(d1, 1/4),
        ] + rollmaker(1, "/", 2, 0.4, "Centre", right=False, rlength=0.3) + [
        LoopEl(d1, -1/4),
        LineEl(0.15, 0.0),
        LineEl(0.1, -0.25),
    ], F3ACentre)
])
