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


class Section(State):
    def __init__(self, data: pd.DataFrame):
        super().__init__(data)

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
    def from_constructs(t, pos, att, bvel, brvel):

        df = pd.DataFrame(index=t, columns=list(State.vars))

        def savevars(vars: list, data: Union[Points, Quaternions]):
            df[vars] = data.to_pandas(columns=vars).set_index(df.index)

        savevars(State.vars.pos, pos)
        savevars(State.vars.att, att)
        savevars(State.vars.bvel, bvel)
        savevars(State.vars.brvel, brvel)

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

        bvel = att.transform_point(pos.diff(dt))
        brvel = att.body_diff(dt)

        return Section.from_constructs(t, pos, att, bvel, brvel)

    def acceleration(self, velconst: str):
        """Generate an acceleration dataframe for the requested velocity data

        Args:
            velocity (pd.DataFrame): 3 columns of the velocity date, index is time
        """
        return Points.from_pandas(
            self.__getattr__(velconst)
        ).diff(
            np.gradient(self.data.index)
        ).to_pandas().set_index(self.data.index)

    def get_state_from_index(self, index):
        return State(self.data.iloc[index])

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

        ipos, iatt, ibvel, ibrvel = initial.handles()
        ivel = initial.transform.rotate(ibvel)

        pos = Points(
            np.array(np.vectorize(
                lambda elapsed: tuple(ipos + elapsed * ivel)
            )(t)).T
        )

        if abs(ibrvel) == 0:
            att = Quaternions.from_quaternion(iatt, len(t))
        else:
            angles = Points.from_point(ibrvel, len(t)) * t
            att = Quaternions.from_quaternion(
                iatt, len(t)).body_rotate(angles)

        bvel = att.transform_point(ivel)

        return Section.from_constructs(t, pos, att, bvel, Points.from_point(ibrvel, len(t)))

    @staticmethod
    def from_radius(initial: State, t: np.array):
        """Generate a section representing a radius. Provide an initial pitch or yaw rate 
        to describe the radius. time array, pitch rates and so on need to be pre-calculated
        for the desired radius and segment

        Assumes there is no aoa or sideslip.


        Args:
            initial (State): The initial State
            t (np.array): the timesteps to create states for

        Returns:
            Section: Section class representing the radius.
        """
        ipos, iatt, ibvel, ibrvel = initial.handles()
        ivel = initial.transform.rotate(ibvel)

        arclength = ibvel.x
        
        
        lpath = ivel.x / t[-1]
        
        
        



    @ staticmethod
    def from_element(element: Element, initial, space):
        """This function will generate a template set of data for a specified element
        and initial condition. The element will be as big as it can be within the supplied
        space.

        Args:
            element (Element): The element to generate, from the schedule description
            initial (Sequence): The previous sequence, last value will be taken as the starting point
            space (?Point?): TBC Limits of an available space, in A/C body frame (Xfwd, Yright, Zdwn)
        """
        pass
