import numpy as np
import pandas as pd
from flightanalysis.section import Section, State
from flightanalysis.section.variables import constructs, missing_constructs
from geometry import Points, Quaternions, Point
from typing import Union
from flightanalysis import FlightLine, Box
from flightdata import Flight, Fields
from pathlib import Path


def make_dt(self: Section) -> np.array:
    return np.gradient(self.data.index)

def make_bvel(self: Section) -> Points:
    wvel = self.gpos.diff(self.gdt)
    return self.gatt.inverse().transform_point(wvel)

def make_brvel(self:Section) -> Points:
    return self.gatt.body_diff(self.gdt).remove_outliers(3) 

def make_bacc(self:Section) -> Points:
    wacc = self.gatt.transform_point(self.gbvel).diff(self.gdt) + Point(0, 0, -9.81) # assumes world Z is up
    return self.gatt.inverse().transform_point(wacc)

def make_bracc(self:Section) -> Points:
    return self.gbrvel.diff(self.gdt)

construct_makers = dict(
    dt=make_dt,
    bvel=make_bvel,
    brvel=make_brvel,
    bacc=make_bacc,
    bracc=make_bracc,
)


def from_constructs(*args,**kwargs):
    kwargs = dict(kwargs, **{list(constructs.keys())[i]: arg for i, arg in enumerate(args)})
    df = pd.concat(
        [constructs[key].todf(x, kwargs["time"]) for key, x in kwargs.items()],
        axis=1
    )

    return Section(df)

def copy(self, *args, **kwargs):
    kwargs = dict(kwargs, **{list(constructs.keys())[i]: arg for i, arg in enumerate(args)})
    
    old_constructs = {key: self.__getattr__("g" + key) for key in self.existing_constructs() if not key in kwargs.keys()}

    new_constructs = {key: value for key, value in list(kwargs.items()) + list(old_constructs.items())}

    return Section.from_constructs(**new_constructs).append_columns(self.data[self.misc_cols()])



def extrapolate_state(istate: State, duration: float, freq: float = None) -> Section:
    t = Section.t_array(duration, freq)

    bvel = Points.from_point(istate.bvel, len(t))

    return Section.from_constructs(
        t,
        pos = Points.from_point(istate.pos,len(t)) + istate.transform.rotate(bvel) * t,
        att = Quaternions.from_quaternion(istate.att, len(t)),
        bvel = bvel
    )

def from_csv(filename) -> Section:
    df = pd.read_csv(filename)

    if "time_index" in df.columns: # This is for back compatability with old csv files where time column was labelled differently
        if "t" in df.columns:
            df.drop("time_index", axis=1)
        else:
            df = df.rename({"time_index":"t"}, axis=1)
    return Section(df.set_index("t", drop=False))


def from_flight(flight: Union[Flight, str], box=Union[FlightLine, Box, str]) -> Section:
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


def _from_flight(flight: Flight, flightline: FlightLine) -> Section:
    # read position and attitude directly from the log(after transforming to flightline)
    t = flight.data.index
    pos = flightline.transform_from.point(
        Points(
            flight.read_numpy(Fields.POSITION).T
        ))

    qs = flight.read_fields(Fields.QUATERNION)
    
    if not pd.isna(qs).all().all():  # for back compatibility with old csv files
        att = flightline.transform_from.quat(
            Quaternions.from_pandas(flight.read_fields(Fields.QUATERNION))
        )
    else:
        att = flightline.transform_from.quat(
            Quaternions.from_euler(Points(
                flight.read_numpy(Fields.ATTITUDE).T
            )))

    # this is EKF velocity estimate in NED frame transformed to contest frame
    vel = flightline.transform_from.rotate(Points(flight.read_numpy(Fields.VELOCITY).T))

    bvel = att.inverse().transform_point(vel)

    bacc = Points(flight.read_numpy(Fields.ACCELERATION).T)

    dt = np.gradient(t)
    brvel = att.body_diff(dt)  
    if pd.isna(qs).all().all():
        brvel = brvel.remove_outliers(2)  # TODO this is a bodge to get rid of phase jumps when euler angles are used directly
    bracc = brvel.diff(dt)

    return Section.from_constructs(t, dt, pos, att, bvel, brvel, bacc, bracc)


def stack(sections: list) -> Section:
    """stack a list of sections on top of each other. last row of each is replaced with first row of the next, 
        indexes are offset so they are sequential

    Args:
        sections (List[Section]): list of sections to stacked

    Returns:
        Section: the resulting Section
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

    return Section(combo)
