from flightplotting import plotsec
from flightanalysis.schedule.definition import *
from flightanalysis.schedule.elements import *
from flightanalysis.criteria import *

p25_def = SchedDef([
    f3amb.create(ManInfo(
            "Triangle", "tri", k=4, position=Position.CENTRE, 
            start=BoxLocation(Height.TOP, Direction.UPWIND, Orientation.INVERTED),
            end=BoxLocation(Height.TOP)
        ),[
            f3amb.loop(np.pi/4),
            f3amb.roll("2x4"),
            f3amb.loop(-np.pi*3/4), 
            f3amb.roll("1/1",line_length="(line_length*1.4142135623730951)"),  # TODO why cany I pass the operation directly?
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
            f3amb.roll("1/2", padded=False),
            f3amb.line(length=30),
            f3amb.roll("1/2", padded=False),
            f3amb.loop(-np.pi),
            f3amb.roll("1/2", padded=False),
        ], loop_radius=80),
    f3amb.create(ManInfo(
            "Humpty", "hB", k=4, position=Position.END, 
            start=BoxLocation(Height.BTM, Direction.DOWNWIND, Orientation.UPRIGHT),
            end=BoxLocation(Height.BTM)
        ),[
            f3amb.loop(np.pi/2),
            f3amb.roll([np.pi/2, -np.pi/2]),
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
        loop_radius=80,
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
        ], line_length=130*np.cos(np.radians(45))),
    f3amb.create(ManInfo(
            "Cloverleaf", "Clv", k=4, position=Position.CENTRE, 
            start=BoxLocation(Height.TOP, Direction.DOWNWIND, Orientation.INVERTED),
            end=BoxLocation(Height.TOP)
        ),[
            f3amb.loop(np.pi/2),
            f3amb.roll("1/2"),
            f3amb.loop(-np.pi*3/2),
            f3amb.roll("1/2", line_length="(loop_radius*2)"),
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
            f3amb.roll("1/2", line_length="(line_length*1.414213562373095)"),
            f3amb.loop(np.pi*5/4),
            f3amb.roll("2x4"),
            f3amb.loop(np.pi/2),
        ]),
    f3amb.create(ManInfo(
            "Spin", "Sp", k=4, position=Position.CENTRE, 
            start=BoxLocation(Height.TOP, Direction.UPWIND, Orientation.INVERTED),
            end=BoxLocation(Height.BTM)
        ),[
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
            f3amb.snap(1, line_length="((100-(1.5*loop_radius))*1.414213562373095)"),
            f3amb.loop(-3*np.pi/4),
        ], loop_radius=30),
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
        ]),
    f3amb.create(ManInfo(
            "Figure S", "S", k=4, position=Position.CENTRE, 
            start=BoxLocation(Height.BTM, Direction.UPWIND, Orientation.UPRIGHT),
            end=BoxLocation(Height.TOP)
        ),[
            f3amb.loop(3*np.pi/4),
            f3amb.loop(np.pi/4, roll=np.pi/2),
            f3amb.loop(3*np.pi/4, ke=True),
            f3amb.loop(np.pi/4, ke=True, roll=np.pi/2),
        ]),
])


if __name__ == "__main__":
    p25, template = p25_def.create_template(170, 1)
    #from flightplotting import plotsec
    
    #plotsec(template, nmodels=100).show()

    fcj = template.create_fc_json(p25_def, "P25")

    from json import dump
    with open("test.json", "w") as f:
        dump(fcj, f)