from flightanalysis.definition import *
from flightanalysis.elements import *
from flightanalysis.scoring.criteria import *
import numpy as np

c45 = np.cos(np.radians(45))


sdef = SchedDef([
    imacmb.create(ManInfo(
            "Q Loop", "qLoop", k=44, position=Position.CENTRE, 
            start=BoxLocation(Height.MID, Direction.UPWIND, Orientation.UPRIGHT),
            end=BoxLocation(Height.BTM)
        ),[
            imacmb.roll([0.125, 0.125, -1.75], rolltypes='rrs', padded=False),
            imacmb.loop(-2*np.pi*7/8),
            imacmb.roll('2x2'),
            imacmb.loop(-np.pi/4)
        ]),
    imacmb.create(ManInfo(
            "Stallturn", "sTurn", k=53, position=Position.END, 
            start=BoxLocation(Height.BTM, Direction.UPWIND, Orientation.INVERTED), 
            end=BoxLocation(Height.BTM)
        ),[
            imacmb.loop(-np.pi/2),
            imacmb.roll([0.25, -1.25], rolltypes='rs'),
            imacmb.stallturn(),
            imacmb.roll('2x4'),
            imacmb.loop(np.pi/2),
        ]),
    imacmb.create(ManInfo(
            "Rolling Circle", "rcirc", k=46, position=Position.CENTRE, 
            start=BoxLocation(Height.BTM, Direction.DOWNWIND, Orientation.UPRIGHT), 
            end=BoxLocation(Height.BTM)
        ),[
            imacmb.loop('directions[0]', ke=True, roll='directions[1]', radius='loop_radius'),
            imacmb.loop('directions[2]', ke=True, roll='directions[3]', radius='loop_radius'),
        ], 
        directions=ManParm('directions', Combination(desired=[
            [np.pi, -2*np.pi, np.pi, 2*np.pi],
            [-np.pi, 2*np.pi, -np.pi, -2*np.pi]
        ]), 1),
        loop_radius=100),
    imacmb.create(ManInfo(
                "Immelman", "Imm", k=39, position=Position.END, 
                start=BoxLocation(Height.BTM, Direction.DOWNWIND, Orientation.UPRIGHT), 
                end=BoxLocation(Height.TOP)
            ),[
                imacmb.roll([3/4, -1/4, -1/4, -1/4], padded=False),
                imacmb.loop(np.pi, radius=100),
                imacmb.snap(1.5, break_angle=np.radians(-15), padded=False),            
            ]
        ),
    imacmb.create(ManInfo(
            "Laydown Humpty", "lhb", k=49, position=Position.CENTRE, 
            start=BoxLocation(Height.TOP, Direction.UPWIND, Orientation.UPRIGHT), 
            end=BoxLocation(Height.TOP)
        ),[
            imacmb.loop(-3*np.pi/4, radius=40),
            imacmb.roll([1.75, -0.25], rolltypes='sr', break_angle=np.radians(-15)),
            imacmb.loop(np.pi, radius=40),
            imacmb.roll('4x4'),
            imacmb.loop(np.pi/8)
        ]
    ),imacmb.create(ManInfo(
            "Double Humpty", "dhb", k=68, position=Position.END, 
            start=BoxLocation(Height.TOP, Direction.UPWIND, Orientation.INVERTED), 
            end=BoxLocation(Height.BTM)
        ),[
            imacmb.spin('directions[0]'),
            imacmb.snap(1),
            imacmb.loop(np.pi),
            imacmb.snap(2),
            imacmb.loop(np.pi),
            imacmb.roll('directions[1]'),
            imacmb.loop(np.pi/2)
        ],
        directions=ManParm('directions', Combination(desired=[
            [1.75, 1.75],
            [-1.75, -1.75]
        ]), 1),
        full_roll_rate=2*np.pi
    ),
    
    
])



if __name__ == "__main__":

 
    sdef.plot().show()
#    f25_def.create_fcj('F25', 'f25_template_fcj.json')
#    sdef.to_json("flightanalysis/data/f25_schedule.json")