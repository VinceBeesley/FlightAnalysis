from flightanalysis.schedule.figure_rules import Categories
from flightanalysis.schedule.element import LineEl, LoopEl, SnapEl, SpinEl, StallTurnEl
from flightanalysis.schedule import Schedule, Manoeuvre, rollmaker, reboundrollmaker, rollsnapcombomaker
import numpy as np

c45 = np.cos(np.radians(45))
mc45 = 1 - c45
r1 = 0.15
d1 = r1*2
r2 = 0.25
d2 = r2 * 2

r3 = 0.21
d3 = r3 * 2
# tkoff
#LineEl( 0.381066, 0.0, 0.0),
f23 = Schedule("F21", Categories.F3A, "upright", -1.0, 0.15, [
    Manoeuvre("loop", 5, [
        LineEl( 0.6, 0.0),
        LineEl( 0.3, 3/4),
        LineEl( 0.1, 0.0),
        LoopEl(0.7, 1.0, 1.0, ke=True),
        LineEl( 0.1, 0.0),
        LineEl( 0.3, 3/4),
    ]),
    Manoeuvre("ST", 4, [
        LineEl( 0.3, 0.0),
        LoopEl( d1, 1/4),
    ] + reboundrollmaker([1.0], 0.6, "Centre", rlength=0.05, snap=True) + [
        StallTurnEl(),
    ] + rollmaker(1, "/", 1, 0.6, "Centre") + [
        LoopEl( d1, 1/4),
    ]),
    Manoeuvre("8pt", 4, [
    ] + rollmaker(8, "X", 8, 1.025, "End") + [
    ]),
    Manoeuvre("shark", 3, [
        LineEl( 0.525, 0.0),
        LoopEl( d1, 1/4),
    ] + rollmaker(3, "X", 4, 0.3, "Centre", rlength=0.25) + [
        LoopEl(d1, -3/8, ke=True),
    ] + rollmaker(3, "/", 4, d1 + 0.3 / c45, "Centre", right=True, rlength=0.25) + [
        LoopEl( d1, -1/8),
    ]),
    Manoeuvre("sql", 5, [
        LineEl( 0.12573593128807187, 0.0),
        LoopEl( d1, -1/8),
    ] + rollmaker(1, "/", 4, 0.3, "Centre") + [
        LoopEl(d1, -1/4, ke=True),
    ] + rollmaker(1, "/", 2, 0.3, "Centre") + [
        LoopEl(d1, 1/4, ke=True),
    ] + rollmaker(1, "/", 2, 0.3, "Centre") + [
        LoopEl(d1, -1/4, ke=True),
    ] + rollmaker(1, "/", 4, 0.3, "Centre") + [
        LoopEl( d1, 1/8),
    ]),
    Manoeuvre("humpty", 4, [
        LineEl( 0.2, 0.0),
        LoopEl( d3, 1/4),
    ] + rollmaker(2, "X", 2, 0.4, "Centre") + [
        LoopEl( d3, -1/2, 1.0),
    ] + reboundrollmaker([1.0], 0.4, "Centre", rlength=0.05, snap=True) + [
        LoopEl( d3, -1/4),
    ]),
    Manoeuvre("h8", 6, [
        LineEl( 0.62 + 0.35, 0.0),
        LoopEl( 0.7, -3/4, 3/4),
        LoopEl(0.7, 1.0, -1.0, ke=True),
        LoopEl(0.7, 1/4, 1/4, ke=True),
    ]),
    Manoeuvre("Et", 3, [
        LineEl( 0.4,  0.0),
        LoopEl( d1, -1/4),
    ] + rollmaker(1, "/", 1, 0.5, "Centre") + [
        LoopEl( d1, -5/8),
    ] + rollmaker(2, "X", 4, (0.5 - d1*c45) / c45, "Centre") + [
        LoopEl( d1, -3/8),
    ]),
    Manoeuvre("u45", 6, [
        LineEl( 0.125 + 0.13404545570494988, 0.0),
        LineEl( 0.1, 1/4),
        LoopEl( d3, -1/8, ke=True),
    ] + reboundrollmaker([1.0, -1.0], 0.9, "Centre", rlength=0.05, snap=True) + [
        LoopEl(d3, 1/8, ke=True),
        LineEl( 0.1, 1/4),
    ]),
    Manoeuvre("rshark", 3, [
        LineEl( 0.2, 0.0),
        LoopEl( d1, -1/4),
    ] + reboundrollmaker([1/2, -1/2], 0.9094112549695433 - 0.15 - d1, "Centre", rlength=0.25, snap=False) + [
        LoopEl( d1, -1/4),
    ] + rollmaker(2, "X", 4, 0.25, "Centre", rlength=0.25) + [
        LoopEl( d1, 3/8),
    ] + rollmaker(1, "/", 1, 0.36, "Centre", rlength=0.25) + [
        LoopEl( d1, -3/8),
    ]),
    Manoeuvre("ft", 6, [
        LineEl( 0.5591168824543141, 0.0),
        LoopEl( d1, -1/8),
    ] + rollmaker(3, "X", 4, 0.5, "Centre", right=True) + [
        LoopEl( d1, 1/2),
    ] + rollmaker(1, "/", 2, 0.5, "Centre") + [
        LoopEl(d1, 1/4, ke=True),
    ] + rollmaker(1, "/", 2, 0.5, "Centre") + [
        LoopEl( d1, 1/2),
    ] + rollmaker(3, "X", 4, 0.5, "Centre", right=False) + [
        LoopEl( d1, -1/8),
    ]),
    Manoeuvre("th", 2, [
        LineEl( 0.8, 0.0),
        LoopEl( d1, -1/4),
    ] + rollmaker(1, "/", 2, 0.4, "Centre") + [
        LoopEl( d1, 1/4),
        LineEl( 0.2, 0.0),
        LoopEl( d1, 1/4),
    ] + rollmaker(1, "/", 2, 0.4, "Centre") + [
        LoopEl( d1, 1/4),
    ]),
    Manoeuvre("spin", 5, [
        LineEl( 0.25 + 0.043207643891886166, 0.0),
        SpinEl(0.05, 2.25, 2.25),
        LineEl( 0.8268790097452905 - 0.15 - r1, 0.0),
        LoopEl( d1, -1/4),
    ]),
    Manoeuvre("cub8", 4,
              reboundrollmaker([0.5, -0.5], 0.85-r3, "End", rlength=0.4) + [
                  LoopEl( d3, -5/8),
              ] + reboundrollmaker([1.5], d3, "Centre", rlength=0.05, snap=True) + [
                  LoopEl( d3, -1/8),
              ]),
    Manoeuvre("circle", 5, [
        LineEl( 0.19603030380329997, 0.0),
        LoopEl(0.7, -0.5, 0.5, ke=True),
        LoopEl(0.7, 0.5, -0.5, ke=True),
    ]),
    Manoeuvre("hsql", 2, [
        LineEl( 0.4, 0.0),
        LoopEl( d1, -1/4),
        ] + reboundrollmaker([0.5, -0.5], 0.8 - d1, "centre", rlength=0.4) + [
        LoopEl( d1, -1/4),
    ]),
    Manoeuvre("av", 5, [
        LineEl( 0.4 + 0.025),
        LoopEl( 0.7, -1/4, 0.5),
        LoopEl( 0.7, 1/4),
        SnapEl(0.05, 1.0),
        LoopEl( 0.7, 1/4),
        LoopEl( 0.7, 1/4, 0.5),
    ]),

])
