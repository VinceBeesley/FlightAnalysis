
from flightanalysis.base import Period, make_dt, make_error
from typing import Union
from flightdata import Flight, Fields
from pathlib import Path
from flightanalysis.base.constructs import Constructs, SVar
from geometry import Point, Quaternion, Quaternions, Points
import numpy as np



contvars = Constructs({
    "time":  SVar("t",         ["t"],         float,      np.array,    make_error, ""),
    "dt":    SVar("dt",        ["dt"],        float,      np.array,    make_dt,    ""),
    "inputs":SVar("inputs",    ["throttle", 
                                "aileron_1", 
                                "aileron_2", 
                                "elevator", 
                                "rudder"
                                ],            np.array,   np.array,    make_error, ""),
})


class Control(Period):
    _cols = contvars
    
class Controls(Period):
    _cols = contvars
    Instant = Control


    def from_flight(flight: Union[Flight, str], control_conversion):
        if isinstance(flight, str):
            flight = {
                ".csv": Flight.from_csv,
                ".BIN": Flight.from_log
            }[Path(flight).suffix](flight)
        t=flight.data.index
        tx_controls = flight.read_fields(Fields.TXCONTROLS).iloc[:,:5]
        tx_controls.columns = ["throttle", "aileron_1", "aileron_2", "elevator", "rudder"]
        for key, value in control_conversion.items():
            tx_controls[key] = value(tx_controls[key])
        return Controls.from_constructs(time=t,inputs=tx_controls.to_numpy())


Control.Period = Controls


cold_draft_conversion = {
     "throttle": lambda pwm: 15 * pwm / 700 - 1500,
    "aileron_1": lambda pwm: 15 * pwm / 700 - 1500, 
    "aileron_2": lambda pwm: 15 * pwm / 700 - 1500, 
    "elevator":  lambda pwm: 15 * pwm / 700 - 1500, 
    "rudder":    lambda pwm: 15 * pwm / 700 - 1500
}