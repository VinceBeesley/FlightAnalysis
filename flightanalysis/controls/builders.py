from . import Controls
from typing import Union
from flightdata import Flight, Fields
from pathlib import Path


control_conversion = {
    "throttle", 
    "aileron_1", 
    "aileron_2", 
    "elevator", 
    "rudder"
}



def from_flight(flight: Union[Flight, str]):
    if isinstance(flight, str):
        flight = {
            ".csv": Flight.from_csv,
            ".BIN": Flight.from_log
        }[Path(flight).suffix](flight)
    t=flight.data.index
    tx_controls = flight.read_fields(Fields.TXCONTROLS).iloc[:,:5]
    tx_controls.columns = ["throttle", "aileron_1", "aileron_2", "elevator", "rudder"]
    return Controls.from_constructs(time=t,inputs=tx_controls.to_numpy())
    
    
    
    #return Controls()