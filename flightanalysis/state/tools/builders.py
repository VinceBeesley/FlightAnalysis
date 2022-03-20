import numpy as np
import pandas as pd
from flightanalysis.state import State

from geometry import Point, Quaternion, PX
from typing import Union
from flightanalysis.flightline import FlightLine, Box
from flightdata import Flight, Fields
from pathlib import Path



def extrapolate(istate: State, duration: float, freq: float = None) -> State:
    t = np.linspace(0,duration, duration * freq)

    bvel = PX(istate.bvel, len(t))

    return State.from_constructs(
        t,
        pos = Point.full(istate.pos,len(t)) + istate.transform.rotate(bvel) * t,
        att = Quaternion.full(istate.att, len(t)),
        bvel = bvel
    )

def from_csv(filename) -> State:
    df = pd.read_csv(filename)

    if "time_index" in df.columns: # This is for back compatability with old csv files where time column was labelled differently
        if "t" in df.columns:
            df.drop("time_index", axis=1)
        else:
            df = df.rename({"time_index":"t"}, axis=1)
    return State(df.set_index("t", drop=False))


def from_flight(flight: Union[Flight, str], box:Union[FlightLine, Box, str]) -> State:
    if isinstance(flight, str):
        flight = {
            ".csv": Flight.from_csv,
            ".BIN": Flight.from_log
        }[Path(flight).suffix](flight)

    if isinstance(box, FlightLine):
        return _from_flight(flight, box)
    if isinstance(box, Box):
        return _from_flight(flight, FlightLine.from_box(box, flight.origin))
    if isinstance(box, str):
        box = Box.from_json(box)
        return _from_flight(flight, FlightLine.from_box(box, flight.origin))
    raise NotImplementedError()


def _from_flight(flight: Flight, flightline: FlightLine) -> State:
    # read position and attitude directly from the log(after transforming to flightline)
    t = flight.data.index
    pos = flightline.transform_from.point(
        Point(
            flight.read_numpy(Fields.POSITION).T
        ))

    qs = flight.read_fields(Fields.QUATERNION)
    
    if not pd.isna(qs).all().all():  # for back compatibility with old csv files
        att = flightline.transform_from.rotate(
            Quaternion(flight.read_fields(Fields.QUATERNION))
        )
    else:
        att = flightline.transform_from.rotate(
            Quaternion.from_euler(Point(
                flight.read_numpy(Fields.ATTITUDE).T
            )))

    # this is EKF velocity estimate in NED frame transformed to contest frame
    vel = flightline.transform_from.rotate(Point(flight.read_numpy(Fields.VELOCITY).T))
    

    bvel = att.inverse().transform_point(vel)

    bacc = Point(flight.read_numpy(Fields.ACCELERATION).T)

    dt = np.gradient(t)

    
    brvel = Point(flight.read_fields(Fields.AXISRATE))
    
    #brvel = att.body_diff(dt)  
    #if pd.isna(qs).all().all():
    #    brvel = brvel.remove_outliers(2)  # TODO this is a bodge to get rid of phase jumps when euler angles are used directly
    bracc = brvel.diff(dt)

    return State.from_constructs(t, dt, pos, att, bvel, brvel, bacc, bracc)


def stack(sections: list) -> State:
    """stack a list of States on top of each other. last row of each is replaced with first row of the next, 
        indexes are offset so they are sequential

    Args:
        States (List[State]): list of States to stacked

    Returns:
        State: the resulting State
    """
    # first build list of index offsets, to be added to each dataframe
    offsets = [0] + [sec.duration for sec in sections[:-1]]
    offsets = np.cumsum(offsets)

    # The sections to be stacked need their last row removed, as the first row of the next replaces it
    dfs = [section.data.iloc[:-1] for section in sections[:-1]] + \
        [sections[-1].data.copy()]

    # offset the df indexes
    for df, offset in zip(dfs, offsets):
        df.index = np.array(df.index) - df.index[0] + offset
    combo = pd.concat(dfs)
    combo.index.name = "t"

    combo["t"] = combo.index

    return State(combo)
