from flightanalysis.schedule.elements import Loop
import numpy as np
from flightanalysis import State
from geometry import Transformation, PX, Point, Euldeg

loop = Loop(30, 50, np.radians(-90), ke=False)
template = loop.create_template(
    State.from_transform(
        Transformation(
            Point(100,150,60),
            Euldeg(180,0,180)
        ), 
        vel=PX(30)
    )    
)

centre = template.arc_centre()

res=loop.intra_scoring.radius(loop, template, template, loop.ref_frame(template))




pass