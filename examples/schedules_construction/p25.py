from flightanalysis.schedule.definition import *
from flightanalysis.schedule.elements import *
from flightanalysis.criteria import *

c45 = np.cos(np.radians(45))



p25_def = SchedDef([
    f3amb.create(ManInfo(
            "Triangle", "tri", k=4, position=Position.CENTRE, 
            start=BoxLocation(Height.TOP, Direction.UPWIND, Orientation.INVERTED),
            end=BoxLocation(Height.TOP)
        ),[
            f3amb.loop(np.pi/4),
            f3amb.roll("2x4"),
            f3amb.loop(-np.pi*3/4), 
            f3amb.roll("1/1",line_length=str(2 * f3amb.mps.line_length * c45)),
            f3amb.loop(-np.pi*3/4),
            f3amb.roll("2x4"),
            f3amb.loop(np.pi/4)
        ], line_length=150),
    f3amb.create(ManInfo(
            "half square", "hsq", k=2, position=Position.END, 
            start=BoxLocation(Height.TOP, Direction.UPWIND, Orientation.INVERTED),
            end=BoxLocation(Height.BTM)
        ),[
            f3amb.loop(np.pi/2),
            f3amb.roll("1/1"),
            f3amb.loop(np.pi/2), 
        ]),
    f3amb.create(ManInfo(
            "Square on Corner", "sqc", k=4, position=Position.CENTRE, 
            start=BoxLocation(Height.BTM, Direction.DOWNWIND, Orientation.UPRIGHT),
            end=BoxLocation(Height.BTM)
        ),[
            f3amb.loop(np.pi/4),
            f3amb.roll("1/2"),
            f3amb.loop(-np.pi/2),
            f3amb.roll("1/2"), 
            f3amb.loop(np.pi/2),
            f3amb.roll("1/2"), 
            f3amb.loop(-np.pi/2),
            f3amb.roll("1/2"), 
            f3amb.loop(np.pi/4),
        ], line_length=80),
    f3amb.create(ManInfo(
            "Figure P", "figP", k=3, position=Position.END, 
            start=BoxLocation(Height.BTM, Direction.DOWNWIND, Orientation.UPRIGHT),
            end=BoxLocation(Height.MID)
        ),[
            f3amb.loop(np.pi/2),
            f3amb.roll("1/2"),
            f3amb.loop(np.pi*3/2),
        ]),
    f3amb.create(ManInfo(
            "Roll Combo", "rc", k=4, position=Position.CENTRE, 
            start=BoxLocation(Height.MID, Direction.UPWIND, Orientation.UPRIGHT),
            end=BoxLocation(Height.MID)
        ),[
            f3amb.roll([np.pi/2, np.pi/2, np.pi/2, -np.pi/2, -np.pi/2, -np.pi/2], padded=False),
        ]),
    f3amb.create(ManInfo(
            "Stall Turn", "st", k=4, position=Position.END, 
            start=BoxLocation(Height.MID, Direction.UPWIND, Orientation.UPRIGHT),
            end=BoxLocation(Height.BTM)
        ),[
            f3amb.loop(np.pi/2),
            f3amb.line(length=50),
            f3amb.stallturn(),
            f3amb.roll("1/2", line_length=180),
            f3amb.loop(-np.pi/2)
        ]),
    f3amb.create(ManInfo(
            "Double Immelman", "Dimm", k=4, position=Position.CENTRE, 
            start=BoxLocation(Height.BTM, Direction.DOWNWIND, Orientation.INVERTED),
            end=BoxLocation(Height.BTM)
        ),[
            f3amb.roll("1/1", padded=False),
            f3amb.loop(-np.pi),
            f3amb.roll("roll_option[0]", padded=False),
            f3amb.line(length=30),
            f3amb.roll("roll_option[1]", padded=False),
            f3amb.loop(-np.pi),
            f3amb.roll("1/2", padded=False),
        ], loop_radius=100, 
        roll_option=ManParm("roll_option", Combination(
            [[np.pi/2, -np.pi/2], [-np.pi/2, np.pi/2]]
        ), 0)),
    f3amb.create(ManInfo(
            "Humpty", "hB", k=4, position=Position.END, 
            start=BoxLocation(Height.BTM, Direction.DOWNWIND, Orientation.UPRIGHT),
            end=BoxLocation(Height.BTM)
        ),[
            f3amb.loop(np.pi/2),
            f3amb.roll([np.pi, -np.pi]),
            f3amb.loop(-np.pi),
            f3amb.roll("1/2"),
            f3amb.loop(np.pi/2),
        ]),
    f3amb.create(ManInfo(
            "Loop", "lP", k=4, position=Position.CENTRE, 
            start=BoxLocation(Height.BTM, Direction.UPWIND, Orientation.UPRIGHT),
            end=BoxLocation(Height.BTM)
        ),[
            f3amb.loop(np.pi/2),
            f3amb.loop(np.pi/2, roll="roll_option[0]"),
            f3amb.loop(-np.pi/2, roll="roll_option[1]"),
            f3amb.loop(np.pi/2),
        ],
        loop_radius=100,
        roll_option=ManParm(
            "roll_option", 
            Combination([[np.pi, -np.pi], [-np.pi, np.pi]]), 0
        )),
    f3amb.create(ManInfo(
            "Half Square on Corner", "hsqc", k=4, position=Position.END, 
            start=BoxLocation(Height.BTM, Direction.UPWIND, Orientation.UPRIGHT),
            end=BoxLocation(Height.TOP)
        ),[
            f3amb.loop(np.pi/4),
            f3amb.roll("1/2"),
            f3amb.loop(-np.pi/2),
            f3amb.roll("1/2"),
            f3amb.loop(np.pi/4),
        ], line_length=130*c45),
    f3amb.create(ManInfo(
            "Cloverleaf", "Clv", k=4, position=Position.CENTRE, 
            start=BoxLocation(Height.TOP, Direction.DOWNWIND, Orientation.INVERTED),
            end=BoxLocation(Height.TOP)
        ),[
            f3amb.loop(np.pi/2),
            f3amb.roll("1/2"),
            f3amb.loop(-np.pi*3/2),
            f3amb.roll("1/2", line_length=str(f3amb.mps.loop_radius * 2)),
            f3amb.loop(np.pi*3/2),
            f3amb.roll("1/2"),
            f3amb.loop(-np.pi/2),
        ]),
    f3amb.create(ManInfo(
            "Figure Et", "Et", k=4, position=Position.END, 
            start=BoxLocation(Height.TOP, Direction.DOWNWIND, Orientation.UPRIGHT),
            end=BoxLocation(Height.TOP)
        ),[
            f3amb.loop(-np.pi/4),
            f3amb.roll("1/2", line_length=str(f3amb.mps.line_length / c45)),
            f3amb.loop(np.pi*5/4),
            f3amb.roll("2x4"),
            f3amb.loop(np.pi/2),
        ]),
    f3amb.create(ManInfo(
            "Spin", "Sp", k=4, position=Position.CENTRE, 
            start=BoxLocation(Height.TOP, Direction.UPWIND, Orientation.INVERTED),
            end=BoxLocation(Height.BTM),
        ),[
            MBTags.CENTRE,
            f3amb.spin(2),
            f3amb.roll("1/2", line_length=165),
            f3amb.loop(np.pi/2),
        ]),
    f3amb.create(ManInfo(
            "Top Hat", "Th", k=4, position=Position.END, 
            start=BoxLocation(Height.BTM, Direction.UPWIND, Orientation.UPRIGHT),
            end=BoxLocation(Height.BTM)
        ),[
            f3amb.loop(np.pi/2),
            f3amb.roll("2x4"),
            f3amb.loop(np.pi/2),
            f3amb.line(length=50),
            f3amb.loop(np.pi/2),
            f3amb.line(),
            f3amb.loop(np.pi/2)
        ]),
    f3amb.create(ManInfo(
            "Figure Z", "Z", k=4, position=Position.CENTRE, 
            start=BoxLocation(Height.BTM, Direction.DOWNWIND, Orientation.UPRIGHT),
            end=BoxLocation(Height.TOP)
        ),[
            f3amb.loop(3*np.pi/4),
            f3amb.snap(1),
            f3amb.loop(-3*np.pi/4),
        ], line_length=60, loop_radius=50),
    f3amb.create(ManInfo(
            "Comet", "Com", k=4, position=Position.END, 
            start=BoxLocation(Height.TOP, Direction.DOWNWIND, Orientation.UPRIGHT),
            end=BoxLocation(Height.BTM)
        ),[
            f3amb.loop(-np.pi/4),
            f3amb.roll("2x4"),
            f3amb.loop(-3*np.pi/2),
            f3amb.roll("1/1"),
            f3amb.loop(np.pi/4),
        ], line_length=(1/c45 + 1) * 50 + 0.5 * 60 - (1/c45 - 2) * 50, loop_radius=50),  
        #2 * R1 + L1 * c45 + 2* R1 * c45 = 4*R2*(1 - c45) - 2*R2 + 2 * L2 * c45
        #(1 / c45 + 1) * R1 + 0.5 * L1 - (1/c45 - 2) * R2 = L2
    f3amb.create(ManInfo(
            "Figure S", "S", k=4, position=Position.CENTRE, 
            start=BoxLocation(Height.BTM, Direction.UPWIND, Orientation.UPRIGHT),
            end=BoxLocation(Height.TOP)
        ),[
            f3amb.loop(3*np.pi/4),
            f3amb.loop(np.pi/4, roll="rke_opt[0]"),
            f3amb.loop("rke_opt[1]", ke=True),
            f3amb.loop("rke_opt[2]", ke=True, roll="rke_opt[3]"),
        ],
        rke_opt=ManParm("rke_opt", 
            Combination([
                [np.pi/2, 3*np.pi/4, np.pi/4, np.pi/2], 
                [-np.pi/2, -3*np.pi/4, -np.pi/4, -np.pi/2]
        ]), 0))
])


if __name__ == "__main__":
    p25, template = p25_def.create_template(170, 1)
    from flightplotting import plotsec
    
#    plotsec(template, nmodels=5).show()

    #fcj = template.create_fc_json(p25_def, "P25")

    p25_def.to_json("flightanalysis/data/p25.json")
