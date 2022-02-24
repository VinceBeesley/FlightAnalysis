
from flightanalysis.base import Period
from .variables import contvars

class Control(Period):
    _cols = contvars
    
class Controls(Period):
    _cols = contvars
    Instant = Control

Control.Period = Controls



from .builders import from_flight

Controls.from_flight = from_flight