from flightdata import Flight, Fields
from geometry import Point, Quaternion, Coord, Transformation, Points, Quaternions, cross_product, GPSPosition
from .flightline import FlightLine, Box
from .state import State
import numpy as np
import pandas as pd
from typing import Tuple, Union
from numbers import Number
from fastdtw import fastdtw
from scipy.spatial.distance import euclidean
from scipy.optimize import minimize
from pathlib import Path
from flightanalysis.wind import wind_vector


class Section():
    _construct_freq = 30

    def __init__(self, data: pd.DataFrame):
        if len(data) == 0:
            raise Exception("Section created with empty dataframe")
        
        
        self.data = data
        self.data.index = self.data.index - self.data.index[0]

    def __getattr__(self, name) -> Union[pd.DataFrame, Points, Quaternions]:
        if name in self.data.columns:
            return self.data[name]
        elif name in State.vars.constructs:
            return self.data[State.vars.constructs[name]]
        elif name in ["gpos", "gbvel", "gbrvel", "gbacc"]:
            return Points.from_pandas(self.__getattr__(name[1:]))
        elif name == "gatt":
            return Quaternions.from_pandas(self.att)
        else:
            raise AttributeError


    def segment(self, partitions):
        parts = np.linspace(self.data.index[0], self.data.index[-1], partitions)

        return [
            self.subset(p0, p1) 
            for p0, p1 in 
            zip(parts[:-2], parts[1:])
        ]

    def subset(self, start: Number, end: Number):
        if start == -1 and not end == -1:
            return Section(self.data.loc[:end])
        elif end == -1 and not start == -1:
            return Section(self.data.loc[start:])
        elif start == -1 and end == -1:
            return Section(self.data)
        else:
            return Section(self.data[start:end])

    @staticmethod
    def stack(sections: list):
        """stack a list of sections on top of each other. last row of each is replaced with first row of the next, 
           indexes are offset so they are sequential

        Args:
            sections (List[Section]): list of sections to stacked

        Returns:
            Section: the resulting Section
        """
        # first build list of index offsets, to be added to each dataframe
        # TODO this assumes the first index of each is 0. should use sec.duration
        offsets = [0] + [sec.duration for sec in sections[:-1]]
        offsets = np.cumsum(offsets)

        # The sections to be stacked need their last row removed,
        # as this is replaced with the first row of the next, data is copied at this point
        dfs = [section.data.iloc[:-1] for section in sections[:-1]] + \
            [sections[-1].data.copy()]

        # offset the df indexes
        for df, offset in zip(dfs, offsets):
            df.index = np.array(df.index) - df.index[0] + offset
        combo = pd.concat(dfs)
        combo.index.name = "time_index"
        return Section(combo)

    @staticmethod
    def from_constructs(t, pos, att, bvel, brvel, bacc):

        df = pd.DataFrame(index=t, columns=list(State.vars))

        def savevars(vars: list, data: Union[Points, Quaternions]):
            df[vars] = data.to_pandas(columns=vars).set_index(df.index)
        
        savevars(State.vars.pos, pos)
        savevars(State.vars.att, att)
        savevars(State.vars.bvel, bvel)
        savevars(State.vars.brvel, brvel)
        savevars(State.vars.bacc, bacc)

        return Section(df)


    def copy(self, t=None, pos:Points=None, att:Quaternions=None, bvel:Points=None, brvel:Points=None, bacc:Points=None):
        if t is None:
            t=self.data.index
        
        pos = self.gpos if pos is None else pos
        sec = Section.from_constructs(
            self.data.index if t is None else t,
            self.gpos if pos is None else pos,
            self.gatt if att is None else att,
            self.gbvel if bvel is None else bvel,
            self.gbrvel if brvel is None else brvel,
            self.gbacc if bacc is None else bacc
        )

        if len(self.data.columns) > len(sec.data.columns):
            missing_cols = list(set(self.data.columns) - set(sec.data.columns))
            sec.data[missing_cols] = self.data[missing_cols].copy()

        return sec

    @staticmethod
    def from_flight(flight: Union[Flight, str], box=Union[FlightLine, Box, str]):
        if isinstance(flight, str):
            flight = {
                ".csv": Flight.from_csv,
                ".BIN": Flight.from_log
            }[Path(flight).suffix](flight)

        if isinstance(box, FlightLine):
            return Section._from_flight(flight, box)
        if isinstance(box, Box):
            return Section._from_flight(flight, FlightLine.from_box(box, flight.origin))
        if isinstance(box, str):
            box = Box.from_json(box)
            return Section._from_flight(flight, FlightLine.from_box(box, flight.origin))
        raise NotImplementedError()

    @staticmethod
    def _from_flight(flight: Flight, flightline: FlightLine):
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

        # brvel = Points.from_pandas(flight.data.loc[:,["axis_rate_roll", "axis_rate_pitch", "axis_rate_yaw"]])

        return Section.from_constructs(t, pos, att, bvel, brvel, bacc)


    def append_columns(self, data):
        df = self.data.copy()        
        df[data.columns] = data
        return Section(df)

    def to_csv(self, filename):
        self.data.to_csv(filename)
        return filename

    def transform(self, transform: Transformation):
        return self.copy(
            pos=transform.point(Points.from_pandas(self.pos)),
            att=transform.quat(Quaternions.from_pandas(self.att)), 
        )

    @staticmethod
    def from_csv(filename):
        return Section(pd.read_csv(filename).set_index("time_index"))

    def __len__(self):
        return len(self.data)

    @property
    def duration(self):
        return self.data.index[-1] - self.data.index[0]

    def get_state_from_index(self, index):
        return State.from_series(self.data.iloc[index].copy())

    def get_state_from_time(self, time):
        return self.get_state_from_index(
            self.data.index.get_loc(time, method='nearest')
        )

    def body_to_world(self, pin: Union[Point, Points]) -> pd.DataFrame:
        """generate world frame trace of a body frame point

        Args:
            pin (Point): point in the body frame
            pin (Points): points in the body frame

        Returns:
            Points: trace of points
        """

        if isinstance(pin, Points) or isinstance(pin, Point):
            return self.gatt.transform_point(pin) + self.gpos
        else:
            return NotImplemented

    @staticmethod
    def t_array(duration: float, freq: float = None):
        if freq==None:
            freq = Section._construct_freq
        return  np.linspace(0, duration, max(int(duration * freq), 3))

    @staticmethod
    def extrapolate_state(istate: State, duration: float, freq: float = None):
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

    def __getitem__(self, key):
        return self.get_state_from_index(key)

    def superimpose_roll(self, proportion: float):
        """Generate a new section, identical to self, but with a continous roll integrated

        Args:
            proportion (float): the amount of roll to integrate
        """
        t = np.array(self.data.index) - self.data.index[0]

        # roll rate to add:
        roll_rate = 2 * np.pi * proportion / t[-1]
        superimposed_roll = t * roll_rate

        # attitude
        angles = Points.from_point(
            Point(1.0, 0.0, 0.0), len(t)) * superimposed_roll

        new_att = Quaternions.from_pandas(self.att.copy()).body_rotate(
            angles)

        axisrates = Points.from_pandas(self.brvel.copy())
        new_rates = Points(np.array([
            np.full(len(t), roll_rate),
            axisrates.y * np.cos(superimposed_roll) +
            axisrates.z * np.sin(superimposed_roll),
            -axisrates.y * np.sin(superimposed_roll) +
            axisrates.z * np.cos(superimposed_roll)
        ]).T)

        acc = Points.from_pandas(self.bacc.copy())
        new_acc = Points(np.array([
            np.zeros(len(t)),
            acc.y * np.cos(superimposed_roll) + acc.z *
            np.sin(superimposed_roll),
            -acc.y * np.sin(superimposed_roll) + acc.z *
            np.cos(superimposed_roll)
        ]).T)

        return Section.from_constructs(
            t,
            Points.from_pandas(self.pos.copy()),
            new_att,
            Points.from_pandas(self.bvel.copy()),
            new_rates,
            new_acc
        )


    def superimpose_rotation(self, axis: Point, angle: float, reference:str="body"):
        """Generate a new section, identical to self, but with a continous rotation integrated       
        """
        t = np.array(self.data.index) - self.data.index[0]

        rate = angle / t[-1]
        superimposed_rotation = t * rate

        angles = Points.from_point(axis.unit(), len(t)) * superimposed_rotation

        if reference=="world":
            new_att = self.gatt.rotate(angles)
        elif reference=="body":
            new_att = self.gatt.body_rotate(angles)
        else:
            raise ValueError("unknwon rotation reference")

        new_bvel = new_att.inverse().transform_point(self.gatt.transform_point(self.gbvel))
            
        dt = np.gradient(t)

        return Section.from_constructs(
            t,
            Points.from_pandas(self.pos.copy()),
            new_att,
            new_bvel,
            new_att.body_diff(dt),
            new_bvel.diff(dt)
        )


    @staticmethod
    def align(flown, template, radius=1):
        3
        fl = flown.brvel.copy()
        fl.brvr = abs(fl.brvr)
        fl.brvy = abs(fl.brvy)

        tp = template.brvel.copy()

        tp.brvr = abs(tp.brvr)
        tp.brvy = abs(tp.brvy)
        distance, path = fastdtw(
            tp.to_numpy(),
            fl.to_numpy(),
            radius=radius,
            dist=euclidean
        )

        mans = pd.DataFrame(path, columns=["template", "flight"]).set_index("template").join(
            template.data.reset_index().loc[:, ["manoeuvre", "element"]]
        ).groupby(['flight']).last().reset_index().set_index("flight")

        return distance, Section(flown.data.reset_index().join(mans).set_index("time_index"))

    def remove_labels(self):
        return Section(self.data.drop(["manoeuvre", "element"], 1, errors="ignore"))

        
    def get_wind(self) -> Points:
        # TODO this should go somewhere else
        def get_wind_error(args: np.ndarray) -> float:
            #wind vectors at the local positions
            local_wind = Points(wind_vector(args[0], np.maximum(self.gpos.z, 0), args[1], args[2]).T)

            #wind vectors in body frame
            body_wind = self.gatt.inverse().transform_point(local_wind)

            #body frame velocity - wind vector should be wind axis velocity
            #error in wind axis velocity, is the non x axis part (because we fly forwards)
            air_vec_error = (self.gbvel - body_wind) * Point(0,1,1)

            #but the wind is only horizontal, so transform to world frame and remove the z component
            world_air_vec_error = self.gatt.transform_point(air_vec_error) * Point(1,1,0)

            #the cost is the cumulative error
            return sum(abs(world_air_vec_error))

        res = minimize(get_wind_error, [np.pi, 5.0, 0.2], method = 'Nelder-Mead')

        return Points(wind_vector(
            res.x[0], 
            np.maximum(self.gpos.z, 0), 
            res.x[1], 
            res.x[2]
        ).T)

    
    def aoa(self):
        bvel = self.gbvel #- self.gatt.inverse().transform_point(self.get_wind())

        df = pd.DataFrame(
            np.array([np.arctan2(bvel.z, bvel.x), np.arctan2(bvel.y, bvel.x)]).T,
            columns=["alpha", "beta"]
            )
        df.index =self.data.index
        return df