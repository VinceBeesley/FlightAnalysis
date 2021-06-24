

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
# tkoff
#Element(ElClass.LINE, 0.381066, 0.0, 0.0),
f23 = Schedule("F21", Categories.F3A, "upright", 1.0, 0.15, [
    Manoeuvre("loop", 5, [
        Element(ElClass.LINE, 0.6, 0.0, 0.0),
        Element(ElClass.LINE, 0.3, 3/4, 0.0),
        Element(ElClass.LINE, 0.1, 0.0, 0.0),
        Element(ElClass.KELOOP, 0.7, 1.0, 1.0),
        Element(ElClass.LINE, 0.1, 0.0, 0.0),
        Element(ElClass.LINE, 0.3, 3/4, 0.0),
    ]),
    Manoeuvre("ST", 4, [
        Element(ElClass.LINE, 0.3, 0.0, 0.0),
        Element(ElClass.LOOP, d1, 0.0, 1/4),
    ] + reboundrollmaker([1.0], 0.6, "Centre", rlength=0.05, snap=True) + [
        Element(ElClass.STALLTURN, 0.05, 0.0, -0.5),
    ] + rollmaker(1, "/", 1, 0.6, "Centre") + [
        Element(ElClass.LOOP, d1, 0.0, 1/4),
    ]),
    Manoeuvre("8pt", 4, [
    ] + rollmaker(8, "X", 8, 1.025, "End") + [
    ]),
    Manoeuvre("shark", 3, [
        Element(ElClass.LINE, 0.525, 0.0, 0.0),
        Element(ElClass.LOOP, d1, 0.0, 1/4),
    ] + rollmaker(3, "X", 4, 0.3, "Centre", rlength=0.25) + [
        Element(ElClass.KELOOP, d1, 0.0, -3/8),
    ] + rollmaker(3, "/", 4, d1 + 0.3 / c45, "Centre", right=True, rlength=0.25) + [
        Element(ElClass.LOOP, d1, 0.0, -1/8),
    ]),
    Manoeuvre("sql", 5, [
        Element(ElClass.LINE, 0.12573593128807187, 0.0, 0.0),
        Element(ElClass.LOOP, d1, 0.0, -1/8),
    ] + rollmaker(1, "/", 4, 0.3, "Centre") + [
        Element(ElClass.KELOOP, d1, 0.0, -1/4),
    ] + rollmaker(1, "/", 2, 0.3, "Centre") + [
        Element(ElClass.KELOOP, d1, 0.0, 1/4),
    ] + rollmaker(1, "/", 2, 0.3, "Centre") + [
        Element(ElClass.KELOOP, d1, 0.0, -1/4),
    ] + rollmaker(1, "/", 4, 0.3, "Centre") + [
        Element(ElClass.LOOP, d1, 0.0, 1/8),
    ]),
    Manoeuvre("humpty", 4, [
        Element(ElClass.LINE, 0.2, 0.0, 0.0),
        Element(ElClass.LOOP, d3, 0.0, 1/4),
    ] + rollmaker(2, "X", 2, 0.4, "Centre") + [
        Element(ElClass.LOOP, d3, 1.0, -1/2),
    ] + reboundrollmaker([1.0], 0.4, "Centre", rlength=0.05, snap=True) + [
        Element(ElClass.LOOP, d3, 0.0, -1/4),
    ]),
    Manoeuvre("h8", 6, [
        Element(ElClass.LINE, 0.62 + 0.35, 0.0, 0.0),
        Element(ElClass.LOOP, 0.7, 3/4, -3/4),
        Element(ElClass.KELOOP, 0.7, 1.0, -1.0),
        Element(ElClass.KELOOP, 0.7, 1/4, 1/4),
    ]),
    Manoeuvre("Et", 3, [
        Element(ElClass.LINE, 0.4, 0.0, 0.0),
        Element(ElClass.LOOP, d1, 0.0, -1/4),
    ] + rollmaker(1, "/", 1, 0.5, "Centre") + [
        Element(ElClass.LOOP, d1, 0.0, -5/8),
    ] + rollmaker(2, "X", 4, (0.5 - d1*c45) / c45, "Centre") + [
        Element(ElClass.LOOP, d1, 0.0, -3/8),
    ]),
    Manoeuvre("u45", 6, [
        Element(ElClass.LINE, 0.125 + 0.13404545570494988, 0.0, 0.0),
        Element(ElClass.LINE, 0.1, 1/4, 0.0),
        Element(ElClass.KELOOP, d3, 0.0, -1/8),
    ] + reboundrollmaker([1.0, -1.0], 0.9, "Centre", rlength=0.05, snap=True) + [
        Element(ElClass.KELOOP, d3, 0.0, 1/8),
        Element(ElClass.LINE, 0.1, 1/4, 0.0),
    ]),
    Manoeuvre("rshark", 3, [
        Element(ElClass.LINE, 0.2, 0.0, 0.0),
        Element(ElClass.LOOP, d1, 0.0, -1/4),
    ] + reboundrollmaker([1/2, -1/2], 0.9094112549695433 - 0.15 - d1, "Centre", rlength=0.25, snap=False) + [
        Element(ElClass.LOOP, d1, 0.0, -1/4),
    ] + rollmaker(2, "X", 4, 0.25, "Centre", rlength=0.25) + [
        Element(ElClass.LOOP, d1, 0.0, 3/8),
    ] + rollmaker(1, "/", 1, 0.36, "Centre", rlength=0.25) + [
        Element(ElClass.LOOP, d1, 0.0, -3/8),
    ]),
    Manoeuvre("ft", 6, [
        Element(ElClass.LINE, 0.5591168824543141, 0.0, 0.0),
        Element(ElClass.LOOP, d1, 0.0, -1/8),
    ] + rollmaker(3, "X", 4, 0.5, "Centre", right=False) + [
        Element(ElClass.LOOP, d1, 0.0, 1/2),
    ] + rollmaker(1, "/", 2, 0.5, "Centre") + [
        Element(ElClass.KELOOP, d1, 0.0, -1/4),
    ] + rollmaker(1, "/", 2, 0.5, "Centre") + [
        Element(ElClass.LOOP, d1, 0.0, 1/2),
    ] + rollmaker(3, "X", 4, 0.5, "Centre", right=True) + [
        Element(ElClass.LOOP, d1, 0.0, -1/8),
    ]),
    Manoeuvre("th", 2, [
        Element(ElClass.LINE, 0.8, 0.0, 0.0),
        Element(ElClass.LOOP, d1, 0.0, -1/4),
    ] + rollmaker(1, "/", 2, 0.4, "Centre") + [
        Element(ElClass.LOOP, d1, 0.0, 1/4),
        Element(ElClass.LINE, 0.2, 0.0, 0.0),
        Element(ElClass.LOOP, d1, 0.0, 1/4),
    ] + rollmaker(1, "/", 2, 0.4, "Centre") + [
        Element(ElClass.LOOP, d1, 0.0, 1/4),
    ]),
    Manoeuvre("spin", 5, [
        Element(ElClass.LINE, 0.25 + 0.043207643891886166, 0.0, 0.0),
        Element(ElClass.SPIN, 0.05, 2.25, -2.25),  # TODO should be 2.25 opp 2.25
        Element(ElClass.LINE, 0.8268790097452905 - 0.15 - r1, 0.0, 0.0),
        Element(ElClass.LOOP, d1, 0.0, -1/4),
    ]),
    Manoeuvre("cub8", 4,
              reboundrollmaker([0.5, -0.5], 0.85-r3, "End", rlength=0.4) + [
                  Element(ElClass.LOOP, d3, 0.0, -5/8),
              ] + reboundrollmaker([1.5], d3, "Centre", rlength=0.05, snap=True) + [
                  Element(ElClass.LOOP, d3, 0.0, -1/8),
              ]),
    Manoeuvre("circle", 5, [
        Element(ElClass.LINE, 0.19603030380329997, 0.0, 0.0),
        Element(ElClass.KELOOP, 0.7, 0.5, -0.5),
        Element(ElClass.KELOOP, 0.7, -0.5, 0.5),
    ]),
    Manoeuvre("hsql", 2, [
        Element(ElClass.LINE, 0.4, 0.0, 0.0),
        Element(ElClass.LOOP, d1, 0.0, -1/4),
        ] + reboundrollmaker([0.5, -0.5], 0.8 - d1, "centre", rlength=0.4) + [
        Element(ElClass.LOOP, d1, 0.0, -1/4),
    ]),
    Manoeuvre("av", 5, [
        Element(ElClass.LINE, 0.4 + 0.025, 0.0, 0.0),
        Element(ElClass.LOOP, 0.7, 0.5, -1/4),
        Element(ElClass.LOOP, 0.7, 0.0, 1/4),
        Element(ElClass.SNAP, 0.05, 1.0, 0.0),
        Element(ElClass.LOOP, 0.7, 0.0, 1/4),
        Element(ElClass.LOOP, 0.7, 0.5, 1/4),
    ]),

])
