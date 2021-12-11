import numpy as np
import pandas as pd
from flightanalysis.section import Section, State
from geometry import Points, Quaternions
from typing import Union
from flightanalysis import FlightLine, Box
from flightdata import Flight, Fields
from pathlib import Path
from flightanalysis.fd_model.atmosphere import Atmosphere, Atmospheres
import warnings


def extrapolate_state(istate: State, duration: float, freq: float = None) -> Section:
    t = Section.t_array(duration, freq)

    bvel = Points.from_point(istate.bvel, len(t))

    return Section.from_constructs(
        t,
        pos = Points.from_point(istate.pos,len(t)) + istate.transform.rotate(bvel) * t,
        att = Quaternions.from_quaternion(istate.att, len(t)),
        bvel = bvel,
        brvel=Points(np.zeros((len(t), 3))),
        bacc=Points(np.zeros((len(t), 3)))
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

    dt = np.gradient(t)

    brvel = att.body_diff(dt)  

    if pd.isna(qs).all().all():
        brvel = brvel.remove_outliers(2)  # TODO this is a bodge to get rid of phase jumps when euler angles are used directly
    
    # this is EKF velocity estimate in NED frame transformed to contest frame
    vel = flightline.transform_from.rotate(Points(flight.read_numpy(Fields.VELOCITY).T))

    bvel = att.inverse().transform_point(vel)

    bacc = Points.from_pandas(
        flight.data.loc[:, ["acceleration_x", "acceleration_y", "acceleration_z"]])

    atm = Atmospheres.from_pandas(flight.read_fields([Fields.PRESSURE, Fields.TEMPERATURE]))

    if atm.count==0:
        warnings.warn("No Atmosphere Data Available, assuming SL Standard pressure and temperature")
        atm=Atmospheres(np.full((len(t), 2), [101325, 288.15]))


    if flight.has_pitot():
        wind = Points.from_pandas(flight.read_fields(Fields.WIND).assign(wind_z=0.0))
        bwind = att.inverse().transform_point(wind)
        return Section.from_constructs(t, pos, att, bvel, brvel, bacc, atm=atm, wind=wind, bwind=bwind).append_flow()
        #arspd = Points.X(flight.read_fields(Fields.AIRSPEED).iloc[:,0].to_numpy())
        #flow = sec.calculate_flow(arspd)
        #return sec.copy(flow=flow)

    else:
        return Section.from_constructs(t, pos, att, bvel, brvel, bacc, atm=atm)


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
