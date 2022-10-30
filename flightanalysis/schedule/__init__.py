"""This module models the aerobatic schedule and the rules that should be applied to it.

It is split into the definition in the ManDef, ManParm and ElDef classes and the 
implementation in the Schedule, Manoeuvre and El classes.

The definition provides a means to describe an aerobatic schedule and the rules that 
should apply to it. It is used to create template implementations and to link
implementations to the relevant cross element scoring criteria.

Criteria are devided into Inter Element and Intra Element. Intra element criteria consider
local changes that can be assessed within the element alone. Inter element criteria
consider the measurements that an element must meet in order to describe an 
aerobatic sequence.

Inter Element Criteria:
    loop element average radius, 
    line element length, 
    line element combined length,
    line element average roll rate,
    average speed, 

Intra Element Criteria:
    Attitude at end of element
    changes in loop radius
    changes in line angle
    loop barreling
    changes in roll rate
    changes in speed
    

Intra element criteria are handled by the element objects themselves. 

Inter element criteria are handled by the ManParm objects, which sit within the 
manoeuvre definition but take measurements of an implementation.


Alignment Process:
1. Create a ScheduleDefinition object 
2. ?? Consider setting the manoeuvre parameters (ManParm defaults) based on measurements of the flight data
3. Create a Schedule object using the default parameters
4. Create a template set of flight data (State object) from the schedule. 
5. Align the template to the flight data using dynamic time warping. 
    This is based on body frame axis rates, absolute roll and yaw rates are used to account for the options
6a. Create a resised Schedule object based on measurements of the aligned elements (dimensions and roll direction options selected)
7. Create a new element matched template based on the element matched schedule
8. ?? Consider repeating steps 5 to 7 with the new template to improve the alignment

Intra Element Judging Process:
1. Manoeuvre initial velocity Vector and roll angle - compare flight to template
2. Element velocity vector and roll angle deviations for lines and lateral only for loops.
    Downgrade anything that takes if further from the initial error at the start of the element.
    Corrections towards correct flight path & roll angle are free to avoid double jeapordy.
3. Loop radius changes
4. Snaps, spins, stallturns?
5. Manoeuvre Final velocity Vector and roll angle - compare flight to template

Inter Element Judging Process
To be described later but it is already implemented in the ManDef

"""



from .elements import Loop, Line, Snap, Spin, StallTurn
from .manoeuvre import Manoeuvre
from .schedule import Schedule
from .definition import *
