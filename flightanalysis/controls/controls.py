
from flightanalysis.base.table import Table, SVar, Time
from typing import Union
from pathlib import Path
from flightanalysis.base.constructs import Constructs, SVar
from geometry import Point, Quaternion, Base
import numpy as np



class Channels(Base):
    cols = ["th", "al", "ar", "e", "r"]


class Actuators(Base):
    cols = ["thr", "ail", "ele", "rud", "flp"]

    @staticmethod
    def from_channels(chans: Channels):
        return Actuators(
            chans.thr, 
            np.mean([chans.al, -chans.ar]), 
            chans.e,
            chans.r,
            np.mean([chans.a1, chans.a2]),
        )


class Controls(Table):
    constructs = Table.constructs + Constructs([
        SVar("actuators", Actuators),
        SVar("channels", Channels)
    ])


    def build(flight, conversion):
        from flightdata import Flight, Fields
        if isinstance(flight, str):
            flight = {
                ".csv": Flight.from_csv,
                ".BIN": Flight.from_log
            }[Path(flight).suffix](flight)
        t=flight.data.index
        controls = Channels(flight.read_fields(Fields.TXCONTROLS).iloc[:,:5])

        return Controls.from_constructs(
            Time.from_t(t.to_numpy()),
            channels=controls,
            surfaces=conversion(controls)
        )


def cold_draft_controls(chans: Channels) -> Actuators:
    """convert a Channels of PWM values to a channels of surface deflections"""

    chs = (chans - chans[0]) / (chans.max() - chans.min())

    return Actuators(
        chs.th,
        np.mean([chs.al, chs.ar], axis=0) * 30,
        chs.e * 30,
        chs.r * 30,
        np.mean([chs.al, -chs.ar], axis=0) * 30
    )


