from flightanalysis.schedule import *
import numpy as np



th = F3AMB.create(
    ManInfo(
        "Top Hat", "tHat", k=4, position=Position.CENTRE, 
        start=BoxLocation(Height.BTM, Direction.UPWIND, Orientation.UPRIGHT),
        end=BoxLocation(Height.BTM)
    ),
    [
        F3AMB.el(Loop, np.pi/2),
        F3AMB.roll("2x4"),
        F3AMB.el(Loop, np.pi/2),
        F3AMB.roll("1/2",l=100),
        F3AMB.el(-np.pi/2),
        F3AMB.roll("2x4"),
        F3AMB.el(-np.pi/2)
    ]
)


