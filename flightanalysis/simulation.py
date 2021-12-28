
"""

Axes:
Judging Axis - X axis in velocity vector, y axis in aircraft xy plane (right wing)
Wind Axis - classic aircraft definition, like judging but offset by environmental wind vector
Body Axis - classic aircraft definition, x axis forward, y axis right wing, z axis down. This is recorded from the 

Pssible Flows:

Schedule -> Section (Judging Axis) + Environment -> Section (Wind Axis) + Model -> Section (Body Axis) + Controls

Section (Judging Axis) + Environment -> Section (Wind Axis)

Section (Wind Axis) + Model -> Section (Body Axis) + Controls

Section (Body Axis) + Controls + model -> Section (Wind Axis)

Section (Wind Axis) - Environment -> Section (Wind Axis)

generally environment and model are not known so:
    
    Derive a model from first principals

    make some assumptions about the model and environment and optimise over flight data to find a result

"""

from flightanalysis import Section
from flightanalysis.environment import Environment

