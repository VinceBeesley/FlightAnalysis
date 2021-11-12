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
from scipy.cluster.vq import whiten
from pathlib import Path
from flightanalysis.wind import wind_vector
from scipy.optimize import minimize, Bounds


import warnings
warnings.filterwarnings("ignore", message="Some columns have standard deviation zero. ")
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
        
        df = pd.concat([
            pd.DataFrame(data=np.array(t), index=t, columns=["flight_time"]), 
            pos.to_pandas(columns=State.vars.pos, index=t), 
            att.to_pandas(columns=State.vars.att, index=t),
            bvel.to_pandas(columns=State.vars.bvel, index=t),
            brvel.to_pandas(columns=State.vars.brvel, index=t),
            bacc.to_pandas(columns=State.vars.bacc, index=t)
        ], axis=1)

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

        return Section.from_constructs(t, pos, att, bvel, brvel, bacc)


    def append_columns(self, data):
        return Section(pd.concat([self.data, data], axis=1, join="inner"))

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

        return self.superimpose_angles(angles, reference)

    def smooth_rotation(self, axis: Point, angle: float, reference:str="body", w: float=0.25, w2=0.1):
        """Accelerate for acc_prop * t, flat rate for middle, slow down for acc_prop * t.

        Args:
            axis (Point): Axis to rotate around.
            angle (float): angle to rotate.
            reference (str, optional): rotate about body or world. Defaults to "body".
            acc_prop (float, optional): proportion of total rotation to be accelerating for. Defaults to 0.1.
        """

        t = np.array(self.data.index) - self.data.index[0]

        T = t[-1]

        V = angle / (T*(1-0.5*w-0.5*w2))  # The maximum rate

        #between t=0 and t=wT
        x = t[t<=w*T]
        angles_0 = (V * x**2) / (2 * w * T)    

        #between t=wT and t=T(1-w)
        y=t[(t>w*T) & (t<=(T-w2*T))]
        angles_1 = V * y - V * w * T / 2
        
        #between t=T(1-w2) and t=T
        z = t[t>(T-w2*T)] - T + w2*T
        angles_2 = V*z - V * z **2 / (2*w2*T) + V*T - V * w2 * T  - 0.5*V*w*T

        angles = Points.from_point(axis.unit(), len(t)) * np.concatenate([angles_0, angles_1, angles_2])

        return self.superimpose_angles(angles, reference)

    def superimpose_angles(self, angles: Points, reference:str="body"): 
        if reference=="world":
            new_att = self.gatt.rotate(angles)
        elif reference=="body":
            new_att = self.gatt.body_rotate(angles)
        else:
            raise ValueError("unknwon rotation reference")

        new_bvel = new_att.inverse().transform_point(self.gatt.transform_point(self.gbvel))
            
        dt = np.gradient(self.data.index)

        sec =  Section.from_constructs(
            np.array(self.data.index),
            Points.from_pandas(self.pos.copy()),
            new_att,
            new_bvel,
            new_att.body_diff(dt),
            new_bvel.diff(dt)
        )
        if "sub_element" in self.data.columns:
            sec = sec.append_columns(self.data["sub_element"])
        return sec


    @staticmethod
    def align(flown, template, radius=1, white=False, weights = Point(1,1,1)):
        """Perform a temporal alignment between two sections. return the flown section with labels 
        copied from the template along the warped path

        Args:
            flown (Section): An un-labelled Section
            template (Section): A labelled Section
            radius (int, optional): The DTW search radius. Defaults to 5.
            whiten (bool, optional): Whether to whiten the data before performing the alignment. Defaults to False.

        """

        def get_brv(brv):
            brv.data[:,0] = abs(brv.data[:,0])
            brv.data[:,2] = abs(brv.data[:,2])

            if white:
                brv = brv.whiten()

            return brv * weights

        fl = get_brv(flown.gbrvel)

        tp = get_brv(template.gbrvel)

        distance, path = fastdtw(
            tp.data,
            fl.data,
            radius=radius,
            dist=euclidean
        )

        return distance, Section.copy_labels(template, flown, path)

    @staticmethod
    def copy_labels(template, flown, path):
        """Copy the labels from a template section to a flown section along the index warping path

        Args:
            template (Section): A labelled section
            flown (Section): An unlabelled section
            path (List): A list of lists containing index pairs from template to flown

        Returns:
            Section: a labelled section
        """
        mans = pd.DataFrame(path, columns=["template", "flight"]).set_index("template").join(
                template.data.reset_index().loc[:, ["manoeuvre", "element"]]
            ).groupby(['flight']).last().reset_index().set_index("flight")

        return Section(flown.data.reset_index().join(mans).set_index("time_index"))

    def label(self, **kwargs):
        return Section(self.data.assign(**kwargs))

    def remove_labels(self):
        return Section(self.data.drop(["manoeuvre", "element"], 1, errors="ignore"))
    
    def wind(self):
        def get_wind_error(args: np.ndarray, sec: Section) -> float:
            #wind vectors at the local positions
            local_wind = Points(wind_vector(head=args[0], h=np.maximum(sec.gpos.z, 0), v0=args[1], a=args[2]).T)

            #wind vectors in body frame
            body_wind = sec.gatt.inverse().transform_point(local_wind)

            #body frame velocity - wind vector should be wind axis velocity
            #error in wind axis velocity, is the non x axis part (because we fly forwards)
            air_vec_error = (sec.gbvel - body_wind) * Point(0,1,1)

            #but the wind is only horizontal, so transform to world frame and remove the z component
            world_air_vec_error = sec.gatt.transform_point(air_vec_error) * Point(1,1,0)

            #the cost is the cumulative error
            return sum(abs(world_air_vec_error))

        bounds = Bounds(lb=[0.0, 0.5, 0.05], ub=[2*np.pi, 20.0, 1.0])
        res = minimize(get_wind_error, [np.pi, 5.0, 0.2], args=self, method = 'Powell', bounds=bounds)

        world_wind = Points(wind_vector(
            head=res.x[0], 
            h=np.maximum(self.pos.z, 0), 
            v0=res.x[1], 
            a=res.x[2]
        ))#.to_pandas(columns=["vwx", "vwy", "vwz"], index=self.data.index)

        body_wind = self.gatt.inverse().transform_point(world_wind)

        return pd.concat(
            [world_wind.to_pandas(prefix="wv", index=self.data.index),
            body_wind.to_pandas(prefix="bwv", index=self.data.index),
            ]
        )

    def aoa(self):
        bvel = self.gbvel #- self.gatt.inverse().transform_point(self.get_wind())

        df = pd.DataFrame(
            np.array([np.arctan2(bvel.z, bvel.x), np.arctan2(bvel.y, bvel.x)]).T,
            columns=["alpha", "beta"]
            )
        df.index =self.data.index
        return df




