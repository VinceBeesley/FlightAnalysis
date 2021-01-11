from flightdata import Flight, Fields
from geometry import Point, Quaternion
from .flightline import FlightLine, Box
from .state import State
import numpy as np
import pandas as pd
from .schedule import Element


# TODO I think this should be called 'Section' or something like that, Sequence can be confused with Schedule.
class Sequence():
    columns = 'x,y,z,dx,dy,dz,dx2,dy2,dz2,rw,rx,ry,rz,drw,drx,dry,drz,drw2,drx2,dry2,drz2'.split(
        ',')

    def __init__(self, data):
        self.data = data

    @staticmethod
    def from_flight(flight: Flight, flightline: FlightLine):
        df = pd.DataFrame(columns=Sequence.columns)
        df.x, df.y, df.z = flightline.transform_to.pos_vec(
            *flight.read_field_tuples(Fields.POSITION))
        df.rw, df.rx, df.ry, df.rz = flightline.transform_to.eul_vec(
            *flight.read_field_tuples(Fields.ATTITUDE))
        df.index = flight.data.index

        dt = pd.Series(df.index).diff()

        for nam in 'x,y,z,rx,ry,rz'.split(','):
            df['d' + nam] = np.vectorize(lambda n,
                                         d: n / d)(df[nam].diff(), dt)
            df['d' + nam +
                '2'] = np.vectorize(lambda n, d: n / d)(df['d' + nam].diff(), dt)

        return Sequence(df.iloc[2:-2])

    def __getattr__(self, name):
        if name in Sequence.columns:
            return self.data[name]
        else:
            raise AttributeError

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
    def from_line(initial: Sequence, length: float, npoints: int):
        df = initial.data.copy()

        return df

    @staticmethod
    def from_element(element: Element, initial, space):
        """This function will generate a template set of data for a specified element
        and initial condition. The element will be as big as it can be within the supplied
        space.

        Args:
            element (Element): The element to generate, from the schedule description
            initial (Sequence): The previous sequence, last value will be taken as the starting point
            space (?Point?): TBC Limits of an available space, in A/C body frame (Xfwd, Yright, Zdwn)
        """

    @staticmethod
    def from_position(pos: Point, att: Quaternion, vel: Point):
        """Generate a Sequence with one datapoint based on defined initial conditions

        Args:
            pos (Point): [description]
            att (Quaternion): [description]
            vel (Point): [description]
        """

        dat = np.zeros(shape=(1, len(Sequence.columns)))
        dat[:, 0:3] = pos.to_list()  # initial position
        dat[:, 3:6] = vel.to_list()  # initial velocity
        # initial attitude (I think)
        dat[:, 9:13] = att.to_list()  # initial attitude

        return Sequence(pd.DataFrame(dat, columns=Sequence.columns))
