from flightdata import Flight, Fields
from geometry import Point, Quaternion, Coord, Transformation, transformation, Points, Quaternions
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
    def from_flight(flight: Flight, flightline: FlightLine):
        # read position and attitude directly from the log(after transforming to flightline)

        df = pd.DataFrame(index=flight.data.index, columns=list(State.vars))

        def savevars(vars: list, data: Union[Points, Quaternions]):
            df[vars] = data.to_pandas(columns=vars).set_index(df.index)
            return data

        pos = savevars(
            State.vars.pos,
            flightline.transform_from.point(
                Points(
                    flight.read_numpy(Fields.POSITION).T
                )))

        att = savevars(
            State.vars.att,
            flightline.transform_from.quat(
                Quaternions.from_euler(Points(
                    flight.read_numpy(Fields.ATTITUDE).T
                ))))

        dt = np.gradient(df.index)

        vel = savevars(State.vars.vel, pos.diff(dt))
        savevars(State.vars.bvel, att.transform_point(vel))
        savevars(State.vars.rvel, att.diff(dt))
        savevars(State.vars.brvel, att.body_diff(dt))

        return Section(df)

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
    def generate(
            initial: State,
            func: Callable[[float], Tuple[float]],
            cols: List[str],
            t1: float,
            npoints: int):
        """Generate a Section by calling the supplied function at npoint intervals between 0 and t1.
        Any column not returned by func will be copied down from the initial state
        Args:
            initial (State): the initial state
            func (Callable): function returns the value of one of the columns in State for 
                            the ratio between 0 and t1 
            cols (list[str]): list of column names returned by func
            t1 (float): The last time value
            npoints (int): number of points to generate

        Returns:
            [Section]: The generated section
        """
        df = pd.DataFrame(initial.data).transpose().reindex(
            np.linspace(0, t1, npoints)
        )

        data = pd.DataFrame(
            np.array(np.vectorize(
                lambda ti: tuple([ti]) + tuple(func(ti / t1))
            )(df.index)).T,
            columns=['t'] + cols
        ).set_index('t')

        df[data.columns] = data
        return Section(df.ffill())

    @staticmethod
    def from_line(initial: State, length: float, npoints: int):
        """generate a section representing a line. 

        Args:
            initial (State): The initial state, the line will be drawn in the direction
                            of the initial velocity vector. 
            length (float): length of the line
            npoints (int): number of points to generate

        Returns:
            Section: Section class representing the line
        """
        vel = Point(*initial.vel)
        pos = Point(*initial.pos)

        return Section.generate(
            initial,
            lambda ratio: pos + vel * ratio,
            list('xyz'),
            length / abs(vel),
            npoints
        )

    @staticmethod
    def from_roll(initial: State, length: float, angle: float, npoints: int):
        """generate a section representing a roll. 
            TODO it would be nice to remove the stuff that is the same as from_line
        Args:
            initial (State): The initial state, the roll will be drawn on a line in the direction
                            of the initial velocity vector. 
            length (float): length of line on which roll occurs
            angle (float): Amount of roll to do, about body X axis so +ve is right
            npoints (int): number of points to generate

        Returns:
            Section: Section class representing a roll
        """
        vel = Point(*initial.vel)
        pos = Point(*initial.pos)
        att = Quaternion(*initial.att)
        t1 = length / abs(vel)
        initial.data['drw,drx,dry,drz'.split(',')] = tuple(
            att * Quaternion.from_euler(
                Point(angle, 0, 0) / t1
            ))
        # generate the roll as an euler angle in the body frame,
        # then rotate it by the initial attitude
        return Section.generate(
            initial,
            lambda ratio: tuple(
                pos + vel * ratio
            ) + tuple(
                att * Quaternion.from_euler(Point(ratio * angle, 0, 0)
                                            )),
            'x,y,z,rw,rx,ry,rz'.split(','),
            t1,
            npoints
        )

    @staticmethod
    def from_radius(initial: State, radius: float, angle: float, npoints: int):
        """Generate a section representing a radius. 
            TODO if angle were 2D this method could represent KE radii
        Args:
            initial (State): The initial State, aircraft heading must align with velocity
                             vector, this is not checked internally
            radius (float): The radius in meters
            angle (float): The amount of rotation in radians. About body frame so positive values 
                            are pulled (up elevator), negative values are pushed (down elevator)
            npoints (int): number of points to generate

        Returns:
            Section: Section class representing the radius.
        """

        vel = Point(*initial.vel)
        pos = Point(*initial.pos)

        centre = initial.body_to_world(Point(0, 0, - radius * np.sign(angle)))
        # Easiest to think about circles in 2D, so generate a transform to and from a
        # coordinate frame, centre on the centre of the arc, x axis pointing to the aircraft,
        # Y axis body forward
        transform = Transformation(
            Coord.from_nothing(),
            Coord.from_xy(
                centre,
                pos - centre,
                initial.body_to_world(Point(1, 0, 0))
            ))

        # generate the roll as an euler angle in the body frame,
        # then rotate it by the initial attitude
        # TODO it would be nice to remove the stuff that is the same as from_line
        return Section.generate(
            initial,
            lambda ratio: tuple(
                transformation.point(
                    radius * (np.cos(ratio / angle) - np.sin(ratio / angle)))
            ) + tuple(

            ),
            State.construct_names('pos', 'att', 'vel', 'rvel', 'acc'),
            angle * radius / abs(vel),
            npoints
        )

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
