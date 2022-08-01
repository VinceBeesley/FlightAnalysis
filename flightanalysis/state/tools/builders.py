import numpy as np
import pandas as pd
from flightanalysis.state import State
from flightanalysis.base.table import Time
from geometry import Point, Quaternion, PX, P0
from typing import Union
from flightanalysis.flightline import FlightLine, Box
from flightdata import Flight, Fields
from pathlib import Path



def extrapolate(istate: State, duration: float) -> State:
    """extrapolate the input state, currently ignores input accelerations

    Args:
        istate (State): initial state of length 1
        duration (float): duration of extrapolation in seconds

    Returns:
        State: state projected forwards
    """

    npoints = np.max([int(np.ceil(duration / istate.time.dt[0])), 3])

    time = Time.from_t(np.linspace(0,duration, npoints))[:-1]
    vel = istate.vel.tile(len(time))   
    rvel = istate.rvel.tile(len(time))
    att = istate.att.body_rotate(rvel * time.t)
    #pos = Point.concatenate([P0(), (att[1:].transform_point(vel[1:]) * time.dt[1:]).cumsum()]) + istate.pos
    pos = (att.transform_point(vel) * time.dt).cumsum() + istate.pos
    return State.from_constructs(time,pos, att, vel, rvel)


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
    """Read position and attitude directly from the log(after transforming to flightline)"""
    time = Time.from_t(np.array(flight.data.time_flight))
    pos = flightline.transform_from.point(Point(flight.read_fields(Fields.POSITION)))
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

    
    vel = att.inverse().transform_point(
        flightline.transform_from.rotate(
            Point(flight.read_numpy(Fields.VELOCITY).T)
        )
    )
    accs=flight.read_fields(Fields.ACCELERATION)
    acc = Point(accs) if not pd.isna(accs).all().all() else None

    rvels=flight.read_fields(Fields.AXISRATE)
    rvel = Point(rvels) if not pd.isna(rvels).all().all() else None
    
    return State.from_constructs(time, pos, att, vel, rvel, acc)


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
