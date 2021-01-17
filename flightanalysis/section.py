from flightdata import Flight, Fields
from geometry import Point, Quaternion
from .flightline import FlightLine, Box
from .state import State
import numpy as np
import pandas as pd
from .schedule import Element
from typing import Dict


# TODO not really happy with the name, not very descriptive.
class Section(State):
    def __init__(self, data: pd.DataFrame):
        super().__init__(data)

    def __getattr__(self, name):
        if name in State.columns:
            return self.data[name].to_numpy()
        elif name in State.constructs:
            return self.data[[State.constructs[name]]].to_numpy()
        else:
            raise AttributeError

    @staticmethod
    def from_flight(flight: Flight, flightline: FlightLine):
        df = pd.DataFrame(columns=State.columns)
        df.x, df.y, df.z = flightline.transform_from.pos_vec(
            *flight.read_field_tuples(Fields.POSITION))
        df.rw, df.rx, df.ry, df.rz = flightline.transform_from.eul_vec(
            *flight.read_field_tuples(Fields.ATTITUDE))
        df.index = flight.data.index

        dt = pd.Series(df.index).diff()

        for nam in 'x,y,z,rx,ry,rz'.split(','):
            df['d' + nam] = np.vectorize(lambda n,
                                         d: n / d)(df[nam].diff(), dt)
            df['d' + nam +
                '2'] = np.vectorize(lambda n, d: n / d)(df['d' + nam].diff(), dt)

        return Section(df.iloc[2:-2])

    def get_state_from_index(self, index):
        return State(self.data.iloc[index])

    def get_state_from_time(self, time):
        return self.get_state_from_index(self.data.get_loc(time, method='nearest'))

    @property
    def pos(self):
        return self.data[['x', 'y', 'z']]

    @property
    def att(self):
        return self.data[['rw', 'rx', 'ry', 'rz']]

    @property
    def vel(self):
        return self.data[['dx', 'dy', 'dz']]

    @property
    def rvel(self):
        return self.data[['drw', 'drx', 'dry', 'drz']]

    @property
    def acc(self):
        return self.data[['dx2', 'dy2', 'dz2']]

    @property
    def racc(self):
        return self.data[['drw2', 'drx2', 'dry2', 'drz2']]

    @staticmethod
    def from_line(initial: State, length: float, npoints: int):
        df = pd.DataFrame(initial.data).transpose()

        t0 = df.index[0]
        vel = Point(*initial.vel)
        t1 = t0 + length / abs(vel)

        df = df.reindex(np.linspace(t0, t0 + length / abs(vel), npoints))

        df['x'], df['y'], df['z'] = np.vectorize(
            lambda ti: (Point(*initial.pos) + vel * ((ti - t0) /
                                                     (t1 - t0))).to_tuple()
        )(df.index)

        return Section(df.ffill())

    def from_roll(initial: State, length: float, angle: float, npoints: int):
        line = Section.from_line(initial, length, npoints)

        initial_att = Quaternion.from_tuple(*initial.att)

        t0 = initial.data.name  # TODO passes the test but not correct
        # Need to deide whether state knows anything about time, or if times
        # for generated sections should be shifted when they are assembled
        t1 = line.data.index[-1]

        # generate the roll as an euler angle in the body frame, then rotate it by the initial attitude
        line.data['rw'], line.data['rx'], line.data['ry'], line.data['rz'] = np.vectorize(
            lambda ti: (Quaternion.from_euler(Point(
                ((ti - t0) /
                 (t1 - t0)) * angle / npoints,
                0,
                0
            )) * initial_att).to_tuple()
        )(line.data.index)

        return line

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
