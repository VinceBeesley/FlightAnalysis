from flightdata import Flight, Fields
from geometry import Point, Quaternion, Coord, Transformation, transformation
from .flightline import FlightLine, Box
from .state import State
import numpy as np
import pandas as pd
from .schedule import Element
from typing import Callable, Tuple, List


# TODO not really happy with the name, not very descriptive.
class Section(State):
    def __init__(self, data: pd.DataFrame):
        super().__init__(data)

    def __getattr__(self, name):
        if name in State.vars:
            return self.data[name].to_numpy()
        elif name in State.vars.constructs:
            return self.data[State.vars.constructs[name]].to_numpy()
        else:
            raise AttributeError

    @staticmethod
    def from_flight(flight: Flight, flightline: FlightLine):
        # read position and attitude directly from the log(after transforming to flightline)

        def makerow(*args):
            pos = flightline.transform_from.point(Point(*args[0:3]))
            att = flightline.transform_from.quat(
                Quaternion.from_euler(Point(*args[3:6])))
            return tuple(pos) + tuple(att)

        df = pd.DataFrame(index=flight.data.index, columns=list(State.vars))
        df[State.vars.pos + State.vars.att] = np.array(
            np.vectorize(makerow)(
                *flight.read_numpy([Fields.POSITION, Fields.ATTITUDE]))
        ).T

        def get_velocity(*args):
            pos1 = Point(*args[0:3])
            att1 = Quaternion(*args[3:7])
            pos2 = Point(*args[7:10])
            att2 = Quaternion(*args[10:14])
            dt = args[14]
            return tuple(pos2 - pos1 / dt) + \
                tuple(Quaternion.axis_rates(att1, att2) / dt) + \
                tuple(Quaternion.body_axis_rates(att1, att2) / dt)

        posatt = df[State.vars.pos + State.vars.att]

        veldata = np.array(
            np.vectorize(get_velocity)(
                *np.column_stack((
                    np.concatenate(
                        [posatt.iloc[:-1].to_numpy(), posatt.iloc[1:].to_numpy()],
                        axis=1
                    ),
                    np.diff(df.index)
                )).T
            ))
        # Copy the last row down and put the whole lot in the dataframe
        df[State.vars.vel + State.vars.rvel +
            State.vars.brvel] = np.column_stack((veldata, veldata[:, -1])).T

        def get_acceleration(*args):
            vel1 = Point(*args[0:3])
            rvel1 = Point(*args[3:6])
            brvel1 = Point(*args[6:9])
            vel2 = Point(*args[9:12])
            rvel2 = Point(*args[12:15])
            brvel2 = Point(*args[15:18])
            dt = args[18]
            return tuple((vel2 - vel1) / dt) + \
                tuple((rvel2 - rvel1) / dt) + \
                tuple((brvel2 - brvel1) / dt)

        vel = df[State.vars.vel + State.vars.rvel + State.vars.brvel]

        accdata = np.array(
            np.vectorize(get_acceleration)(
                *np.column_stack((
                    np.concatenate(
                        [vel.iloc[:-1].to_numpy(), vel.iloc[1:].to_numpy()],
                        axis=1
                    ),
                    np.diff(df.index)
                )).T
            ))
        # Copy the last row down and put the whole lot in the dataframe
        df[State.vars.acc + State.vars.racc +
            State.vars.bracc] = np.column_stack((accdata, accdata[:, -1])).T

        return Section(df)

    def get_state_from_index(self, index):
        return State(self.data.iloc[index])

    def get_state_from_time(self, time):
        return self.get_state_from_index(self.data.get_loc(time, method='nearest'))

    def body_to_world(self, pin: Point) -> pd.DataFrame:
        """generate world frame trace of a body frame point 

        Args:
            pin (Point): point in the body frame

        Returns:
            pd.DataFrame: trace of points
        """
        df = self.data.apply(
            lambda row: tuple(State(row).body_to_world(pin)),
            axis=1,
            result_type='expand'
        )

        # pd.DataFrame(
        #    np.array(np.vectorize(
        #        lambda row: State(row).body_to_world(pin)
        #    )(self.data)).T,
        #    columns=list('xyz')
        # )
        df.index = self.data.index
        return df

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
