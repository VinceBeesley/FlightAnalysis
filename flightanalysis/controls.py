
from flightanalysis.base.table import Table, SVar, Time
from typing import Union
from flightdata import Flight, Fields
from pathlib import Path
from flightanalysis.base.constructs import Constructs, SVar
from geometry import Point, Quaternion, Base
import numpy as np



class Channels(Base):
    cols = ["thr", "al", "ar", "e", "r"]


class Surfaces(Base):
    cols = ["thr", "ail", "ele", "rud", "flp"]

    @staticmethod
    def from_channels(chans: Channels):
        return Surfaces(
            chans.thr, 
            np.mean([chans.al, -chans.ar]), 
            chans.e,
            chans.r,
            np.mean([chans.a1, chans.a2]),
        )


class Controls(Table):
    constructs = Table.constructs + Constructs(dict(
        surfaces = SVar(Surfaces),
        channels = SVar(Channels)
    ))


    def build(flight: Union[Flight, str], control_conversion):
        if isinstance(flight, str):
            flight = {
                ".csv": Flight.from_csv,
                ".BIN": Flight.from_log
            }[Path(flight).suffix](flight)
        t=flight.data.index
        tx_controls = flight.read_fields(Fields.TXCONTROLS).iloc[:,:5]
        tx_controls.columns = ["throttle", "aileron_1", "aileron_2", "elevator", "rudder"]
        for key, value in control_conversion.items():
            tx_controls.loc[:,key] = value(tx_controls[key])


        return Controls.from_constructs(time=t,deflection=tx_controls.to_numpy())


def cold_draft_controls(Channels):
    """convert a Channels of PWM values to a channels of surface deflections"""
    pass


