

from flightanalysis.schedule import Schedule, Manoeuvre, Element, ElClass, Categories, rollmaker
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
        Element(ElClass.LINE, 0.8, 0.0, 0.0),
        Element(ElClass.LINE, 0.2, 0.5, 0.0),
        Element(ElClass.LOOP, 0.45, 0.0, 1.0),
        Element(ElClass.LOOP, 0.45, 0.0, -1.0),
        Element(ElClass.LINE, 0.2, 0.5, 0.0),
    ]),
    Manoeuvre("stall", 3, [
        Element(ElClass.LINE, 0.3, 0.0, 0.0),
        Element(ElClass.LOOP, 0.3, 0.0, 0.25),
        Element(ElClass.LINE, 0.25, 0.0, 0.0),
        Element(ElClass.STALLTURN, 0.05, 0.0, 0.0)
    ] + rollmaker(2, "X", 4, 0.7, "Centre") + [
        Element(ElClass.LOOP, 0.3, 0.0, -0.25)
    ]),
    Manoeuvre("sqL", 4, [
        Element(ElClass.LINE, 0.5, 0.0, 0.0),
        Element(ElClass.LOOP, 0.4, 0.0, -0.125),
        Element(ElClass.LINE, 0.3, 0.0, 0.0),
        Element(ElClass.LOOP, 0.4, 0.0, -0.25)
    ] + rollmaker(1, "/", 2, 0.3, "Centre") + [
        Element(ElClass.LOOP, 0.4, 0.0, 0.25),
        Element(ElClass.LINE, 0.3, 0.0, 0.0),
        Element(ElClass.LOOP, 0.4, 0.0, 0.25)
    ] + rollmaker(1, "/", 2, 0.3, "Centre") + [
        Element(ElClass.LOOP, 0.4, 0.0, -0.125)
    ]),
    Manoeuvre("9", 4, [
        Element(ElClass.LINE, 0.35, 0.0, 0.0),
        Element(ElClass.LOOP, 0.4, 0.0, -0.25),
        Element(ElClass.LINE, 0.05, 0.0, 0.0),
        Element(ElClass.LINE, 0.2, 0.5, 0.0),
        Element(ElClass.LINE, 0.2, -0.5, 0.0),
        Element(ElClass.LINE, 0.05, 0.0, 0.0),
        Element(ElClass.LOOP, 0.4, 0.0, 0.75),
    ]),  # 0.35+0.2+0.2 = 0.75, h =0.1+0.2+ 0.5 -0.2=0.6
    Manoeuvre("ke", 5, [
        Element(ElClass.LINE,  0.25,  0.0,  0.0),  # 0.5
        Element(ElClass.LINE, 0.1, 0.25, 0.0),  # 0.4
        Element(ElClass.LINE, 0.2, -0.5, 0.0),  # 0.2
        Element(ElClass.LINE, 0.4, 0.0, 0.0),  # -0.2
        Element(ElClass.LINE, 0.2, -0.5, 0.0),  # -0.4
        Element(ElClass.LINE, 0.1, 0.25, 0.0)]  # -0.5
    ),
    Manoeuvre("sS", 2, [
        Element(ElClass.LINE, 0.25, 0.0, 0.0),  # -0.75
        Element(ElClass.LOOP, 0.5, 0.0, 0.5),  # h=0.1
        Element(ElClass.LINE, 0.15, 0.5, 0.0),  # -0.6
        Element(ElClass.LINE, 0.05, 0.0, 0.0),  # -0.55
        Element(ElClass.LINE, 0.15, 0.5, 0.0)]  # -0.4
    ),
    Manoeuvre("golf", 5, [
        Element(ElClass.LINE, 0.12, 0.0, 0.0),
        Element(ElClass.LOOP, 0.45, 0.0, 0.125),
        Element(ElClass.LINE, 0.28 / c45, 0.0, 0.0),
        Element(ElClass.LOOP, 0.45, 0.0, 0.125),
        Element(ElClass.LOOP, 0.45, 0.5, 0.5),
        Element(ElClass.LOOP, 0.45, 0.0, -0.125),
        Element(ElClass.LINE, 0.28 / c45, 0.0, 0.0),
        Element(ElClass.LOOP, 0.45, 0.0, -0.125)]
    ),
    Manoeuvre("sFin", 3, [
        Element(ElClass.LINE, 0.57, 0.0, 0.0),
        Element(ElClass.LOOP, d1, 0.0, -0.25),
        Element(ElClass.LINE, 0.25, 0.0, 0.0),
        Element(ElClass.LOOP, d1, 0.0, -0.375)
    ] + rollmaker(2, "X", 4,
                  (0.25 + 2 * r1 * c45) / c45,
                  "Centre") + [
        Element(ElClass.LOOP, 0.3, 0.0, -0.125)]  # 1 - r1 - l1 - 2rc45
    ),
    Manoeuvre("dImm", 5, [
        Element(ElClass.LINE, 1.1 - 0.25 - r1 - 4 * r1 * c45, 0.0, 0.0),  # 0.1
        Element(ElClass.LINE, 0.2, 0.5, 0.0),
        Element(ElClass.LOOP, 0.6,  0.0,  0.5),
    ] + rollmaker(4, "X", 8, 0.6, "Start") + [
        Element(ElClass.LOOP,  0.6,  0.0,  -0.5),
        Element(ElClass.LINE,  0.2,  0.5,  0.0)]  # 0.1
    ),
    Manoeuvre("hB", 3, [
        Element(ElClass.LINE,  0.55,  0.0,  0.0),  # 0.45
        Element(ElClass.LOOP,  0.3,  0.0,  0.25), # 0.6
    ] + rollmaker(1, "/", 2, 0.5, "Centre") + [ 
        Element(ElClass.LOOP,  0.3,  0.0,  0.5),  # 0.9
        Element(ElClass.LINE,  0.5,  0.0,  0.0),
        Element(ElClass.LOOP,  0.3,  0.0,  0.25)] # 0.75
    ),
    Manoeuvre("rollC", 3, [
        Element(ElClass.LINE,  0.35,  0.0,  0.0),  # 0.4
        Element(ElClass.LINE,  0.2,  0.5,  0.0), # -0.2
        Element(ElClass.LINE,  0.4,  -1.0,  0.0), # +0.2
        Element(ElClass.LINE,  0.2,  0.5,  0.0)] # +0.4
    ),
    Manoeuvre("tHat", 3, [
        Element(ElClass.LINE,  0.395,  0.0,  0.0),  # 0.795
        Element(ElClass.LOOP,  0.3,  0.0,  0.25),
    ] + rollmaker(1, "/", 2, 0.5, "Centre") + [ 
        Element(ElClass.LOOP,  0.3,  0.0,  -0.25),
        Element(ElClass.LINE,  0.3182076438918871,  0.0,  0.0), # 0.46320764389188707
        Element(ElClass.SPIN,  0.05,  2.5,  0.0), # [0.47, 0.5637655569733979, 0.8516980890270289]
        Element(ElClass.LINE,  0.601698089027029,  0.0,  0.0),
        Element(ElClass.LOOP,  0.3,  0.0,  -0.25)] # 0.27
    ),
    Manoeuvre("Z", 3, [
        Element(ElClass.LINE,  0.37,  0.0,  0.0), #0.05
        Element(ElClass.LOOP,  d1,  0.0,  -0.375),
        ] + rollmaker(1, "/", 1, 2 * (0.05 + r1 * c45) / c45, "Centre") + [ 
        Element(ElClass.LOOP,  d1,  0.0,  0.375)]  # 0.05, h=0.9242640687119287
    ),
    Manoeuvre("com", 3, [
        Element(ElClass.LINE,  0.325,  0.0,  0.0), # 0.275
        Element(ElClass.LOOP,  0.3,  0.0,  0.125), 
        Element(ElClass.LINE,  0.15,  0.0,  0.0),
        Element(ElClass.LINE,  0.1,  0.25,  0.0),
        Element(ElClass.LINE,  0.1,  -0.25,  0.0),
        Element(ElClass.LINE,  0.15,  0.0,  0.0),
        Element(ElClass.LOOP,  0.3,  0.0,  -0.75),
        Element(ElClass.LINE,  0.15,  0.0,  0.0),
        Element(ElClass.LINE,  0.2,  0.5,  0.0),
        Element(ElClass.LINE,  0.15,  0.0,  0.0),
        Element(ElClass.LOOP,  0.3,  0.0,  -0.125)]  # 0.275
    ),
    Manoeuvre("4pt", 3, [
        Element(ElClass.LINE,  0.06,  0.0,  0.0), # 0.21
        Element(ElClass.LINE,  0.07,  0.25,  0.0),
        Element(ElClass.LINE,  0.05,  0.0,  0.0),
        Element(ElClass.LINE,  0.07,  0.25,  0.0),
        Element(ElClass.LINE,  0.05,  0.0,  0.0),
        Element(ElClass.LINE,  0.07,  0.25,  0.0),
        Element(ElClass.LINE,  0.05,  0.0,  0.0),
        Element(ElClass.LINE,  0.07,  0.25,  0.0)] #0.21, h=0.34142135623730985
    ),
    Manoeuvre("hsq", 3, [
        Element(ElClass.LINE,  0.2,  0.0,  0.0),
        Element(ElClass.LOOP,  0.3,  0.0,  -0.125),
        ] + rollmaker(1, "/", 4, 0.24, "Centre") + [ 
        Element(ElClass.KELOOP,  0.3,  0.0,  -0.25),
        ] + rollmaker(1, "/", 4, 0.24, "Centre", True) + [ 
        Element(ElClass.LOOP,  0.3,  0.0,  -0.125)]  # 0.4149999999999997,
    ),
    Manoeuvre("aV", 3, [
        Element(ElClass.LINE,  0.4399999999999997,  0.0,  0.0),
        Element(ElClass.LOOP,  0.7,  0.0,  -0.5),
        Element(ElClass.SNAP,  0.05,  1.0,  0.5),
        Element(ElClass.LOOP,  0.7,  0.0,  -0.5)]
    )
])


