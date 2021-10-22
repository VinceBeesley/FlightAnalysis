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
from scipy import optimize
from pathlib import Path
import warnings

class Section():
    _construct_freq = 30

    def __init__(self, data: pd.DataFrame):
        if len(data) == 0:
            raise Exception("Section created with empty dataframe")
            #warnings.warn("Creating a Section with empty data is likely to cause downstream errors")
        self.data = data

    def __getattr__(self, name):
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


    def aoa(self):
        bvel = self.gbvel
        return np.tan(bvel.z / bvel.x), np.tan(bvel.y / bvel.x)

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
        vel = flightline.transform_to.rotate(Points.from_pandas(
            flight.data.loc[:, ["velocity_x", "velocity_y", "velocity_z"]]))
        bvel = att.inverse().transform_point(vel)

        bacc = Points.from_pandas(
            flight.data.loc[:, ["acceleration_x", "acceleration_y", "acceleration_z"]])

        # brvel = Points.from_pandas(flight.data.loc[:,["axis_rate_roll", "axis_rate_pitch", "axis_rate_yaw"]])

        return Section.from_constructs(t, pos, att, bvel, brvel, bacc)

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
        data = pd.read_csv(filename)
        data.index = data["time_index"].copy()
        return Section(data)

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
            return Quaternions.from_pandas(self.att).transform_point(pin) + Points.from_pandas(self.pos)
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
            pos = Points.from_point(istate.pos,len(t)) + istate.back_transform.rotate(bvel) * t,
            att = Quaternions.from_quaternion(istate.att, len(t)),
            bvel = bvel,
            brvel=Points(np.zeros((len(t), 3))),
            bacc=Points(np.zeros((len(t), 3)))
        )


    @staticmethod
    def from_line(itransform: Transformation, speed: float, length: float, freq: float = None):
        """generate a section representing a line. Provide an initial rotation rate to represent a roll.

        Args:
            initial (State): The initial state, the line will be drawn in the direction
                            of the initial velocity vector.
            t (np.array): the timesteps to create states for
        Returns:
            Section: Section class representing the line or roll.
        """
        
        
        t = Section.t_array(duration=length / speed, freq=freq)
        ibvel = Point(speed, 0.0, 0.0)
        bvel = Points.from_point(ibvel, len(t))

        pos = Points.from_point(itransform.translation,len(t)) + itransform.rotate(bvel) * t

        att = Quaternions.from_quaternion(itransform.rotation, len(t))

        return Section.from_constructs(
            t,
            pos,
            att,
            bvel,
            Points(np.zeros((len(t), 3))),
            Points(np.zeros((len(t), 3)))
        )

    @staticmethod
    def from_loop(itransform: Transformation, speed: float, proportion: float, radius: float, ke: bool = False, freq: float = _construct_freq):
        """generate a loop, based on intitial position, speed, amount of loop, radius. 

        Args:
            itransform (Transformation): initial position
            speed (float): forward speed
            proportion (float): amount of loop. +ve offsets centre of loop in +ve body y or z
            r (float): radius of the loop (must be +ve)
            ke (bool, optional): [description]. Defaults to False. whether its a KE loop or normal

        Returns:
            [type]: [description]
        """
        duration = 2 * np.pi * radius * abs(proportion) / speed
        axis_rate = -proportion * 2 * np.pi / duration
        if freq==None:
            freq = Section._construct_freq
        t = np.linspace(0, duration, max(int(duration * freq), 3))

        # TODO There must be a more elegant way to do this.
        if axis_rate == 0:
            raise NotImplementedError()
        radius = speed / axis_rate
        if not ke:
            radcoord = Coord.from_xy(
                itransform.point(Point(0, 0, -radius)),
                itransform.rotate(Point(0, 0, 1)),
                itransform.rotate(Point(1, 0, 0))
            )
            angles = Points.from_point(Point(0, axis_rate, 0), len(t)) * t
            radcoordpoints = Points(
                np.array(np.vectorize(
                    lambda angle: tuple(Point(
                        radius * np.cos(angle),
                        radius * np.sin(angle),
                        0
                    ))
                )(angles.y)).T
            )
            axisrates = Points.from_point(Point(0, axis_rate, 0), len(t))
            acceleration = -Points.from_point(cross_product(
                Point(0, axis_rate, 0) * Point(0, axis_rate, 0), Point(speed, 0, 0)), len(t))
        else:
            radcoord = Coord.from_xy(
                itransform.point(Point(0, -radius, 0)),
                itransform.rotate(Point(0, 1, 0)),
                itransform.rotate(Point(1, 0, 0))
            )
            angles = Points.from_point(Point(0, 0, -axis_rate), len(t)) * t
            radcoordpoints = Points(
                np.array(np.vectorize(
                    lambda angle: tuple(Point(
                        radius * np.cos(-angle),
                        radius * np.sin(-angle),
                        0
                    ))
                )(angles.z)).T
            )
            axisrates = Points.from_point(Point(0, 0, -axis_rate), len(t))
            acceleration = Points.from_point(cross_product(
                Point(0, 0, axis_rate) * Point(0, 0, axis_rate), Point(speed, 0, 0)), len(t))

        return Section.from_constructs(
            t,
            Transformation.from_coords(
                Coord.from_nothing(), radcoord).point(radcoordpoints),
            Quaternions.from_quaternion(
                itransform.rotation, len(t)).body_rotate(angles),
            Points.from_point(Point(speed, 0, 0), len(t)),
            axisrates,
            acceleration
        )

    @staticmethod
    def from_spin(itransform: Transformation, height: float, turns: float, opp_turns: float = 0.0, freq: float = _construct_freq):
        inverted = np.sign(itransform.rotate(Point(0, 0, 1)).z)

        nose_drop = Section.from_loop(
            itransform, 5.0, -0.25 * inverted, 2.0, False)

        nose_drop.data["sub_element"] = "nose_drop"

        rotation = Section.from_line(
            nose_drop.get_state_from_index(-1).transform,
            5.0,
            height-2.5,
            freq
        ).superimpose_roll(turns)

        rotation.data["sub_element"] = "rotation"

        if opp_turns == 0.0:
            return Section.stack([nose_drop, rotation])
        else:
            rotation2 = Section.from_line(
                rotation.get_state_from_index(-1).transform,
                5.0,
                height-2.5
            ).superimpose_roll(opp_turns)

            rotation2.data["sub_element"] = "opp_rotation"

            return Section.stack([nose_drop, rotation, rotation2])

    @staticmethod
    def from_snap(itransform: Transformation, speed: float, length: float, rolls: float, negative=False):
        pass


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


    def superimpose_rotation(self, axis: Point, amount: float):
        """Generate a new section, identical to self, but with a continous rotation integrated

        Args:
            proportion (float): the amount of roll to integrate
        """
        t = np.array(self.data.index) - self.data.index[0]

        # roll rate to add:
        rate =2* np.pi * amount / t[-1]
        superimposed_rotation = t * rate

        angles = Points.from_point(axis.unit(), len(t)) * superimposed_rotation

        new_att = self.gatt.body_rotate(angles)

        new_bvel = new_att.transform_point(self.gatt.inverse().transform_point(self.gbvel))
            
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
