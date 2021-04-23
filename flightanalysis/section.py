from flightdata import Flight, Fields
from geometry import Point, Quaternion, Coord, Transformation, transformation, Points, Quaternions, cross_product
from numpy.testing._private.utils import assert_equal
from .flightline import FlightLine, Box
from .state import State
import numpy as np
import pandas as pd
from .schedule import Element
from typing import Callable, Tuple, List, Union
from numbers import Number
from .schedule import Schedule, Manoeuvre, Element


class Section():
    def __init__(self, data: pd.DataFrame):
        self.data = data

    def __getattr__(self, name):
        if name in State.vars:
            return self.data[name]
        elif name in State.vars.constructs:
            return self.data[State.vars.constructs[name]]
        else:
            raise AttributeError

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
    def stack(sections):
        offsets = [0] + [sec.data.index[-1] for sec in sections[:-1]]

        dfs = [section.data.iloc[:-1] for section in sections[:-1]] + \
            [sections[-1].data.copy()]

        for df, offset in zip(dfs, np.cumsum(offsets)):
            df.index = np.array(df.index) + offset

        return Section(pd.concat(dfs))

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

    @staticmethod
    def from_flight(flight: Flight, flightline: FlightLine):
        # read position and attitude directly from the log(after transforming to flightline)
        t = flight.data.index
        pos = flightline.transform_from.point(
            Points(
                flight.read_numpy(Fields.POSITION).T
            ))

        att = flightline.transform_from.quat(
            Quaternions.from_euler(Points(
                flight.read_numpy(Fields.ATTITUDE).T
            )))

        dt = np.gradient(t)

        brvel = att.body_diff(dt)
        vel = flightline.transform_to.rotate(Points.from_pandas(flight.data.loc[:, ["velocity_x", "velocity_y", "velocity_z"]]))
        bvel = att.inverse().transform_point(vel)

        bacc = Points.from_pandas(flight.data.loc[:,["acceleration_x", "acceleration_y", "acceleration_z"]])

        #brvel = Points.from_pandas(flight.data.loc[:,["axis_rate_roll", "axis_rate_pitch", "axis_rate_yaw"]])

        return Section.from_constructs(t, pos, att, bvel, brvel, bacc)

    def get_state_from_index(self, index):
        return State.from_series(self.data.iloc[index])

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
    def from_line(initial: State, t: np.array):
        """generate a section representing a line. Provide an initial rotation rate to represent a roll. 

        Args:
            initial (State): The initial state, the line will be drawn in the direction
                            of the initial velocity vector. 
            t (np.array): the timesteps to create states for
        Returns:
            Section: Section class representing the line or roll.
        """

        pos = Points(
            np.array(np.vectorize(
                lambda elapsed: tuple(initial.pos + elapsed * initial.vel)
            )(t)).T
        )

        if abs(initial.brvel) == 0:
            att = Quaternions.from_quaternion(initial.att, len(t))
        else:
            angles = Points.from_point(initial.brvel, len(t)) * t
            att = Quaternions.from_quaternion(
                initial.att, len(t)).body_rotate(angles)

        bvel = att.transform_point(initial.vel)

        return Section.from_constructs(t, pos, att, bvel, Points.from_point(initial.brvel, len(t)))

    @staticmethod
    def from_radius(initial: State, t: np.array):
        """Generate a section representing a radius. 

        Args:
            initial (State): The initial State
            t (np.array): the timesteps to create states for

        Returns:
            Section: Section class representing the radius.
        """

        radius = initial.bvel.x / initial.brvel.y
        radcoord = Coord.from_xy(
            initial.transform.point(Point(0, 0, -radius)),
            initial.transform.rotate(Point(0, 0, 1)),
            initial.transform.rotate(Point(1, 0, 0))
        )
        angles = Points.from_point(initial.brvel, len(t)) * t

        radcoordpoints = Points(
            np.array(np.vectorize(
                lambda angle: tuple(Point(
                    radius * np.cos(angle),
                    radius * np.sin(angle),
                    0
                ))
            )(angles.y)).T
        )

        return Section.from_constructs(
            t,
            Transformation.from_coords(
                Coord.from_nothing(), radcoord).point(radcoordpoints),
            Quaternions.from_quaternion(
                initial.att, len(t)).body_rotate(angles),
            Points.from_point(initial.bvel, len(t)),
            Points.from_point(initial.brvel, len(t))
        )

    @staticmethod
    def from_element(initial: State, element: Element):
        """This function will generate a template set of data for a specified element
        and initial condition. The element will be as big as it can be within the supplied
        space.

        Args:
            element (Element): The element to generate, from the schedule description
            initial (Sequence): The previous sequence, last value will be taken as the starting point
            space (?Point?): TBC Limits of an available space, in A/C body frame (Xfwd, Yright, Zdwn)
        """
        pass

    @staticmethod
    def from_manoeuvre(last_state: State, manoeuvre: Manoeuvre):
        elms = []
        for element in manoeuvre.elements:
            elms.append(Section.from_element(element, last_state))
            last_state = elms[-1].get_state_from_index(-1)
        return elms

    @staticmethod
    def from_schedule(last_state: State, schedule: Schedule):
        elms = []
        for manoeuvre in schedule.manoeuvres:
            elms += Section.from_manoeuvre(last_state, manoeuvre)
            last_state = elms[-1].get_state_from_index(-1)
        return Section.stack(elms)
