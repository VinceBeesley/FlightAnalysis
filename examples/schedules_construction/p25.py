from flightanalysis.schedule.definition import *
from flightanalysis.schedule.elements import *
from flightanalysis.schedule.scoring.criteria import *
import numpy as np

c45 = np.cos(np.radians(45))



p25_def = SchedDef([
    f3amb.create(ManInfo(
            "Triangle", "trgle", k=3, position=Position.CENTRE, 
            start=BoxLocation(Height.TOP, Direction.UPWIND, Orientation.INVERTED),
            end=BoxLocation(Height.TOP)
        ),[
            MBTags.CENTRE,
            f3amb.loop(np.pi/4),
            f3amb.roll("2x4"),
            f3amb.loop(-np.pi*3/4), 
            centred(f3amb.roll("1/1",line_length=str(2 * c45 * f3amb.mps.line_length))),
            f3amb.loop(-np.pi*3/4),
            f3amb.roll("2x4"),
            f3amb.loop(np.pi/4),
            MBTags.CENTRE
        ], line_length=150),
    f3amb.create(ManInfo(
            "half square", "hSqL", k=2, position=Position.END, 
            start=BoxLocation(Height.TOP, Direction.UPWIND, Orientation.INVERTED),
            end=BoxLocation(Height.BTM)
        ),[
            f3amb.loop(np.pi/2),
            f3amb.roll("1/1"),
            f3amb.loop(np.pi/2), 
        ]),
    f3amb.create(ManInfo(
            "Square on Corner", "sqL", k=5, position=Position.CENTRE, 
            start=BoxLocation(Height.BTM, Direction.DOWNWIND, Orientation.UPRIGHT),
            end=BoxLocation(Height.BTM)
        ),[
            MBTags.CENTRE,
            f3amb.loop(np.pi/4),
            f3amb.roll("1/2"),
            f3amb.loop(-np.pi/2),
            f3amb.roll("1/2"), 
            centred(f3amb.loop(np.pi/2)),
            f3amb.roll("1/2"), 
            f3amb.loop(-np.pi/2),
            f3amb.roll("1/2"), 
            f3amb.loop(np.pi/4),
            MBTags.CENTRE
        ], line_length=80),
    f3amb.create(ManInfo(
            "Figure P", "fig9", k=3, position=Position.END, 
            start=BoxLocation(Height.BTM, Direction.DOWNWIND, Orientation.UPRIGHT),
            end=BoxLocation(Height.MID)
        ),[
            f3amb.loop(np.pi/2),
            f3amb.roll("1/2"),
            f3amb.loop(np.pi*3/2),
        ]),
    f3amb.create(ManInfo(
            "Roll Combo", "rollC", k=4, position=Position.CENTRE, 
            start=BoxLocation(Height.MID, Direction.UPWIND, Orientation.UPRIGHT),
            end=BoxLocation(Height.MID)
        ),[
            centred(f3amb.roll([np.pi/2, np.pi/2, np.pi/2, -np.pi/2, -np.pi/2, -np.pi/2], padded=False)),
        ]),
    f3amb.create(ManInfo(
            "Stall Turn", "stall", k=3, position=Position.END, 
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
            "Double Immelman", "dImm", k=4, position=Position.CENTRE, 
            start=BoxLocation(Height.BTM, Direction.DOWNWIND, Orientation.INVERTED),
            end=BoxLocation(Height.BTM)
        ),[
            f3amb.roll(2*np.pi, padded=False),
            f3amb.loop(-np.pi),
            f3amb.roll("roll_option[0]", padded=False),
            centred(f3amb.line(length=30)),
            f3amb.roll("roll_option[1]", padded=False),
            f3amb.loop(-np.pi),
            f3amb.roll(np.pi, padded=False),
        ], loop_radius=100, 
        roll_option=ManParm("roll_option", Combination(
            desired=[[-np.pi/2, np.pi/2], [np.pi/2, -np.pi/2]]
        ), 0)),
    f3amb.create(ManInfo(
            "Humpty", "hB", k=3, position=Position.END, 
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
            "Loop", "loop", k=5, position=Position.CENTRE, 
            start=BoxLocation(Height.BTM, Direction.UPWIND, Orientation.UPRIGHT),
            end=BoxLocation(Height.BTM)
        ),[
            f3amb.loop(np.pi/2),
            f3amb.loop(np.pi/2, roll="roll_option[0]"),
            MBTags.CENTRE,
            f3amb.loop(-np.pi/2, roll="roll_option[1]"),
            f3amb.loop(np.pi/2),
        ],
        loop_radius=100,
        roll_option=ManParm(
            "roll_option", 
            Combination(desired=[[np.pi, -np.pi], [-np.pi, np.pi]]), 0
        )),
    f3amb.create(ManInfo(
            "Half Square on Corner", "hSqL2", k=2, position=Position.END, 
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
            "Cloverleaf", "hClov", k=5, position=Position.CENTRE, 
            start=BoxLocation(Height.TOP, Direction.DOWNWIND, Orientation.INVERTED),
            end=BoxLocation(Height.TOP)
        ),[
            f3amb.loop(np.pi/2),
            MBTags.CENTRE,
            f3amb.roll("1/2"),
            f3amb.loop(-np.pi*3/2),
            centred(f3amb.roll("1/2", line_length=str(f3amb.mps.loop_radius * 2))),
            f3amb.loop(np.pi*3/2),
            MBTags.CENTRE,
            f3amb.roll("1/2"),
            f3amb.loop(-np.pi/2),
        ]),
    f3amb.create(ManInfo(
            "Figure Et", "rEt", k=4, position=Position.END, 
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
            "Spin", "iSpin", k=3, position=Position.CENTRE, 
            start=BoxLocation(Height.TOP, Direction.UPWIND, Orientation.INVERTED),
            end=BoxLocation(Height.BTM),
        ),[
            MBTags.CENTRE,
            f3amb.spin(2),
            f3amb.roll("1/2", line_length=165),
            f3amb.loop(np.pi/2),
        ]),
    f3amb.create(ManInfo(
            "Top Hat", "tHat", k=3, position=Position.END, 
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
            centred(f3amb.snap(1)),
            f3amb.loop(-3*np.pi/4),
        ], line_length=60, loop_radius=50),
    f3amb.create(ManInfo(
            "Comet", "Com", k=3, position=Position.END, 
            start=BoxLocation(Height.TOP, Direction.DOWNWIND, Orientation.UPRIGHT),
            end=BoxLocation(Height.BTM)
        ),[
            f3amb.loop(-np.pi/4),
            f3amb.roll("2x4"),
            f3amb.loop(-3*np.pi/2),
            f3amb.roll("1/1"),
            f3amb.loop(np.pi/4),
        ], line_length=(1/c45 + 1) * 50 + 30 - (1/c45 - 2) * 50, loop_radius=50),  
    f3amb.create(ManInfo(
            "Figure S", "figS", k=5, position=Position.CENTRE, 
            start=BoxLocation(Height.BTM, Direction.UPWIND, Orientation.UPRIGHT),
            end=BoxLocation(Height.TOP)
        ),[
            MBTags.CENTRE,
            f3amb.loop(3*np.pi/4),
            f3amb.loop(np.pi/4, roll="rke_opt[0]"),
            MBTags.CENTRE,
            f3amb.loop("rke_opt[1]", ke=True),
            f3amb.loop("rke_opt[2]", ke=True, roll="rke_opt[3]"),
            MBTags.CENTRE
        ],
        rke_opt=ManParm("rke_opt", 
            Combination(desired=[
                [np.pi/2, 3*np.pi/4, np.pi/4, np.pi/2], 
                [-np.pi/2, -3*np.pi/4, -np.pi/4, -np.pi/2]
        ]), 0))
])


if __name__ == "__main__":

#    p25_def.plot().show()
    #p25_def.create_fcj('P25', 'p25_template_fcj.json')
    p25_def.to_json("flightanalysis/data/p25_schedule.json")