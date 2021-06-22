

from flightanalysis.schedule import Schedule, Manoeuvre, Element, ElClass, Categories, rollmaker, reboundrollmaker, rollsnapcombomaker
import numpy as np

c45 = np.cos(np.radians(45))
mc45 = 1 - c45
r1 = 0.15
d1 = r1*2
r2 = 0.25
d2 = r2 * 2

r3 = 0.21
d3 = r3 * 2


f21 = Schedule("F21", Categories.F3A, "upright", 1.0, 0.15, [
    Manoeuvre("golf", 4, [
        Element(ElClass.LINE, 1.081066, 0.0, 0.0),
        Element(ElClass.LOOP, d1, 0.0, -3/8),
    ] + rollmaker(3, "/", 4, 0.45, "Centre") + [
        Element(ElClass.KELOOP, d1, 0.0, -3/8),
        Element(ElClass.SNAP, 0.05, 1.0, 0.0),
        Element(ElClass.KELOOP, d1, 0.0, -3/8),
    ] + rollmaker(3, "/", 4, 0.45, "Centre", right=True) + [
        Element(ElClass.LOOP, d1, 0.0, -3/8),
    ]),
    Manoeuvre("cub8", 3, [
        Element(ElClass.LINE, 0.1, 0.0, 0.0),
        Element(ElClass.LOOP, d2, 0.0, -1/8),
    ] + reboundrollmaker([0.25, 0.25, -0.25], 2*r2, "Centre") + [
        Element(ElClass.KELOOP, d2, 0.0, 5/8),
        Element(ElClass.LINE, 0.3, 0.75, 0.0),
    ]),
    Manoeuvre("circle", 4, [
        Element(ElClass.LINE, 0.4260407468305834, 0.0, 0.0),
        Element(ElClass.KELOOP, 0.7, 0.5, -1/2),
        Element(ElClass.KELOOP, 0.7, -0.5, 1/2),
    ]),
    Manoeuvre("tHat", 4, [
        Element(ElClass.LINE, 0.4, 0.0, 0.0),
        Element(ElClass.LOOP, d1, 0.0, 0.25),
    ] + rollmaker(3, "X", 4, 0.5, "Centre", right=False) + [
        Element(ElClass.LOOP, d1, 0.0, -0.25),
        Element(ElClass.LINE, 0.1, 0.0, 0.0),
        Element(ElClass.LOOP, d1, 0.0, -0.25),
    ] + reboundrollmaker([3/4], 0.5, "Centre", snap=True) + [
        Element(ElClass.LOOP, d1, 0.0, -0.25),
    ]),
    Manoeuvre("hB", 5, [
        Element(ElClass.LINE, 0.2, 0.0, 0.0),
        Element(ElClass.LOOP, d1+0.1, -0.25, -0.25),
    ] + rollmaker(1, "/", 1, 0.5, "Centre", right=False) + [
        Element(ElClass.LOOP, d1+0.1, 0.0, 0.5),
    ] + reboundrollmaker([0.5, -0.5], 0.5, "Centre") + [
        Element(ElClass.KELOOP, d1+0.1, 0.25, -0.25),
    ]),
    Manoeuvre("v8", 5, [
        Element(ElClass.LINE, 0.3, 0.0, 0.0),
        Element(ElClass.LOOP, d3, 0.0, 3/8),
        Element(ElClass.LOOP, d3, 0.25, 1/8),
        Element(ElClass.KELOOP, d3, 0.25, -1/8),
        Element(ElClass.LOOP, d3, 0.0, 7/8),
    ]),
    Manoeuvre("stall", 4, [
        Element(ElClass.LINE, 0.5+r3 - 0.006792356108113501, 0.0, 0.0),
        Element(ElClass.LOOP, d3, 0.0, -3/4),
    ] + reboundrollmaker([0.25, -0.5], 0.6, "Centre") + [
        Element(ElClass.STALLTURN, 0.05, 0.0, 0.0),
    ] + rollmaker(3, "/", 4, 0.6, "Centre", right=False) + [
        Element(ElClass.LOOP, d3, 0.0, 3/4),
    ]),
    Manoeuvre("9", 4, [
        Element(ElClass.LINE, 1.0396229316756604 + 0.006792356108113501, 0.0, 0.0),
        Element(ElClass.LOOP, d1, 0.0, -3/4),
        Element(ElClass.LINE, 0.16, 0.0, 0.0),
        Element(ElClass.SNAP, 0.1, 1.5, 0.0),
        Element(ElClass.LINE, 0.16, 0.0, 0.0),
        Element(ElClass.LOOP, d1, 0.0, -1/4),
    ]),
    Manoeuvre("tHat2", 6, [
        Element(ElClass.LINE, 0.05, 0.0, 0.0),
        Element(ElClass.LOOP, d1, 0.0, -1/4),
    ] + rollmaker(3, "/", 4, 0.4, "Centre", right=False, rlength=0.3) + [
        Element(ElClass.KELOOP, d1, 0.0, -1/4),
    ] + rollmaker(1, "/", 1, 0.4, "Centre", right=False, rlength=0.3) + [
        Element(ElClass.KELOOP, d1, 0.0, -1/4),
    ] + rollmaker(1, "/", 4, 0.4, "Centre", right=False, rlength=0.3) + [
        Element(ElClass.LOOP, d1, 0.0, -1/4),
    ]),
    Manoeuvre("hSqL", 3, [
    ] + rollmaker(1, "/", 2, 0.35, "End", right=False, rlength=0.3) + [
        Element(ElClass.LOOP, d1, 0.0, 1/4),
    ] + reboundrollmaker([0.5, -1.0], 0.55, "Centre", rlength=0.3) + [
        Element(ElClass.LOOP, d1, 0.0, -1/4),
    ]),
    Manoeuvre("45Line", 6, [
        Element(ElClass.LINE, 0.35 + 0.012867965644036, 0.0, 0.0),
        Element(ElClass.LOOP, d1, 0.0, -1/8),
    ] + rollsnapcombomaker([
        ("roll", 0.25),
        ("snap", 1.0),
        ("snap", -1.0),
        ("roll", -0.25)], (0.85 - 2*r1*mc45) / c45, "Centre", rlength=0.4) + [
        Element(ElClass.LOOP, d1, 0.0, 1/8),
    ]),
    Manoeuvre("8loop", 3, [
        Element(ElClass.LINE, 0.05, 0.0, 0.0),
        Element(ElClass.LOOP, d1, 0.0, 1/8),
    ] + rollmaker(1, "/", 2, 0.2, "Centre", right=False, rlength=0.3) + [
        Element(ElClass.LOOP, d1, 0.0, -1/8),
        Element(ElClass.LINE, 0.2, 0.0, 0.0),
        Element(ElClass.LOOP, d1, 0.0, -1/8),
    ] + rollmaker(1, "/", 2, 0.2, "Centre", right=False, rlength=0.3) + [
        Element(ElClass.LOOP, d1, 0.0, 1/8),
    ]),
    Manoeuvre("loop", 5, [
        Element(ElClass.LINE, 0.5371320343559636, 0.0, 0.0),
        Element(ElClass.LOOP, 0.782842712474619, 1.0, 1/2),
        Element(ElClass.LOOP, 0.782842712474619, -1.0, 1/2),
    ]),
    Manoeuvre("spin", 3, [
        Element(ElClass.LINE, 0.95, 0.0, 0.0),
        Element(ElClass.SPIN, 0.06, 2.5, 0.0),
        Element(ElClass.LINE, 0.5745408015016459, 0.0, 1/2),
        Element(ElClass.LOOP, d1, 0.0, -0.25),
    ]),
    Manoeuvre(
        "rollC",
        3,
        reboundrollmaker([0.5,-0.25, -0.25, -0.25, -0.25, 0.5], 0.8067923561081121 + 0.45, "End", rlength=0.3)
    ),
    Manoeuvre("fTurn", 4, [
        Element(ElClass.LINE, 0.05, 0.0, 0.0),
        Element(ElClass.LOOP, d1, 0.0, -1/8),
        ] + rollmaker(3, "/", 4, 0.4, "Centre", right=False, rlength=0.3) + [
        Element(ElClass.LOOP, d1, 0.0, 0.5),
        ] + reboundrollmaker([-0.75], 0.4, "Centre", rlength=0.05, snap=True) + [
        Element(ElClass.LOOP, d1, 0.0, -1/8),
    ]),
    Manoeuvre("square", 4, [
        Element(ElClass.LINE, 0.45, 0.0, 0.0),
        Element(ElClass.LINE, 0.1, -0.25, 0.0),
        Element(ElClass.LINE, 0.15, 0.0, 0.0),
        Element(ElClass.LOOP, d1, 0.0, 1/4),
        ] + rollmaker(1, "/", 2, 0.4, "Centre", right=False, rlength=0.3) + [
        Element(ElClass.LOOP, d1, 0.0, -1/4),
        ] + rollmaker(1, "/", 2, 0.4, "Centre", right=False, rlength=0.3) + [
        Element(ElClass.LOOP, d1, 0.0, 1/4),
        ] + rollmaker(1, "/", 2, 0.4, "Centre", right=False, rlength=0.3) + [
        Element(ElClass.LOOP, d1, 0.0, -1/4),
        Element(ElClass.LINE, 0.15, 0.0, 0.0),
        Element(ElClass.LINE, 0.1, -0.25, 0.0),
    ])
])
