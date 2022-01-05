from .flightline import FlightLine, Box
from .section import Section, State
from .schedule import (
    Schedule,
    Manoeuvre,
    Loop,
    Line,
    Snap,
    Spin,
    StallTurn,
    Categories, 
    rules,
    get_schedule
)

def get_q(rho, v):
    return 0.5 * rho * v**2



from .fc_json import FCJson


